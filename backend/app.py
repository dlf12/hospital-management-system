# --- 导入必要的库 ---
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import or_, func
import json

# 1. 创建 Flask 应用实例
app = Flask(__name__)

# 2. 允许跨域请求
CORS(app)

# 3. 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1/hospital_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "1943860229"

# 4. 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# --- 数据模型定义 ---

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    id_card = db.Column(db.String(18), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone_number = db.Column(db.String(20))
    department = db.Column(db.String(50), nullable=False, default='内科')  # 新增：科室字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增：创建时间

    records = db.relationship('MedicalRecord', backref='patient', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'id_card': self.id_card,
            'age': self.age,
            'gender': self.gender,
            'phone_number': self.phone_number,
            'department': self.department,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment_plan = db.Column(db.Text, nullable=False)
    record_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'diagnosis': self.diagnosis,
            'treatment_plan': self.treatment_plan,
            'record_date': self.record_date.strftime('%Y-%m-%d %H:%M:%S'),
            'patient_id': self.patient_id
        }

class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_shared = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    owner = db.relationship('User', backref='templates')

    def to_dict(self):
        try:
            content_parsed = json.loads(self.content)
        except Exception:
            content_parsed = self.content
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'content': content_parsed,
            'owner_id': self.owner_id,
            'is_shared': self.is_shared,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }

def get_current_user():
    identity = get_jwt_identity()
    if not identity:
        return None
    return User.query.filter_by(username=identity).first()

# --- API 接口定义 ---

# -- 认证接口 --
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "用户名已存在"}), 409

    new_user = User()
    new_user.set_password(password)
    new_user.username = username
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "注册成功"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

    return jsonify({"message": "用户名或密码错误"}), 401

# -- 病人接口 (受保护) --
@app.route('/api/patients', methods=['GET'])
@jwt_required()
def get_patients():
    # 搜索参数
    search_query = request.args.get('search', '').strip()
    # 科室筛选参数
    department = request.args.get('department', '').strip()
    # 分页参数
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    try:
        per_page = min(100, max(1, int(request.args.get('per_page', 20))))
    except ValueError:
        per_page = 20

    query = Patient.query

    # 按科室筛选
    if department:
        query = query.filter(Patient.department == department)

    # 按搜索条件筛选
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(or_(
            Patient.name.like(search_term),
            Patient.id_card.like(search_term),
            Patient.phone_number.like(search_term)
        ))

    # 分页查询
    pagination = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    items = [patient.to_dict() for patient in pagination.items]
    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page
    })

@app.route('/api/patients', methods=['POST'])
@jwt_required()
def add_patient():
    data = request.get_json()

    # 验证必填字段
    if not data.get('name') or not data.get('id_card'):
        return jsonify({'message': '姓名和身份证号不能为空'}), 400

    # 检查身份证号是否已存在
    if Patient.query.filter_by(id_card=data['id_card']).first():
        return jsonify({'message': '该身份证号已存在'}), 409

    # 验证科室
    valid_departments = ['内科', '外科', '妇产科', '儿科']
    department = data.get('department', '内科')
    if department not in valid_departments:
        return jsonify({'message': '无效的科室'}), 400

    new_patient = Patient(
        name=data['name'],
        id_card=data['id_card'],
        age=data.get('age'),
        gender=data.get('gender', '男'),
        phone_number=data.get('phone_number'),
        department=department
    )

    try:
        db.session.add(new_patient)
        db.session.commit()
        return jsonify(new_patient.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '添加病人失败'}), 500

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()

    # 检查身份证号是否被其他病人使用
    if data.get('id_card') and data['id_card'] != patient.id_card:
        existing = Patient.query.filter(
            Patient.id_card == data['id_card'],
            Patient.id != patient_id
        ).first()
        if existing:
            return jsonify({'message': '该身份证号已被其他病人使用'}), 409

    # 验证科室
    if data.get('department'):
        valid_departments = ['内科', '外科', '妇产科', '儿科']
        if data['department'] not in valid_departments:
            return jsonify({'message': '无效的科室'}), 400

    # 更新字段
    patient.name = data.get('name', patient.name)
    patient.id_card = data.get('id_card', patient.id_card)
    patient.age = data.get('age', patient.age)
    patient.gender = data.get('gender', patient.gender)
    patient.phone_number = data.get('phone_number', patient.phone_number)
    patient.department = data.get('department', patient.department)

    try:
        db.session.commit()
        return jsonify(patient.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '更新病人信息失败'}), 500

@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    try:
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': '删除病人成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '删除病人失败'}), 500

# -- 病历接口 (受保护) --
@app.route('/api/patients/<int:patient_id>/records', methods=['GET'])
@jwt_required()
def get_records_for_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(
        MedicalRecord.record_date.desc()
    ).all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/patients/<int:patient_id>/records', methods=['POST'])
@jwt_required()
def add_record_for_patient(patient_id):
    Patient.query.get_or_404(patient_id)  # 确保病人存在
    data = request.get_json()

    if not data or not data.get('diagnosis') or not data.get('treatment_plan'):
        return jsonify({'message': '诊断信息和治疗方案不能为空'}), 400

    new_record = MedicalRecord(
        diagnosis=data['diagnosis'],
        treatment_plan=data['treatment_plan'],
        patient_id=patient_id
    )

    try:
        db.session.add(new_record)
        db.session.commit()
        return jsonify(new_record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '添加病历失败'}), 500

# -- 模板接口 (受保护) --
@app.route('/api/templates', methods=['GET'])
@jwt_required()
def list_templates():
    user = get_current_user()
    only_mine = request.args.get('mine', 'true').lower() == 'true'

    query = Template.query
    if only_mine:
        query = query.filter((Template.owner_id == user.id) | (Template.is_shared == True))

    templates = query.order_by(Template.updated_at.desc()).all()
    return jsonify([t.to_dict() for t in templates])

@app.route('/api/templates', methods=['POST'])
@jwt_required()
def create_template():
    user = get_current_user()
    data = request.get_json() or {}

    name = data.get('name')
    content = data.get('content')
    if not name or content is None:
        return jsonify({'message': '模板名称和内容不能为空'}), 400

    tpl = Template(
        name=name,
        description=data.get('description'),
        content=json.dumps(content) if not isinstance(content, str) else content,
        owner_id=user.id,
        is_shared=bool(data.get('is_shared', False))
    )

    try:
        db.session.add(tpl)
        db.session.commit()
        return jsonify(tpl.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '创建模板失败'}), 500

@app.route('/api/templates/<int:tpl_id>', methods=['GET'])
@jwt_required()
def get_template(tpl_id):
    tpl = Template.query.get_or_404(tpl_id)
    return jsonify(tpl.to_dict())

@app.route('/api/templates/<int:tpl_id>', methods=['PUT'])
@jwt_required()
def update_template(tpl_id):
    user = get_current_user()
    tpl = Template.query.get_or_404(tpl_id)

    if tpl.owner_id != user.id:
        return jsonify({'message': '无权限修改该模板'}), 403

    data = request.get_json() or {}
    tpl.name = data.get('name', tpl.name)
    tpl.description = data.get('description', tpl.description)

    if 'content' in data:
        tpl.content = json.dumps(data['content']) if not isinstance(data['content'], str) else data['content']

    tpl.is_shared = bool(data.get('is_shared', tpl.is_shared))

    try:
        db.session.commit()
        return jsonify(tpl.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '更新模板失败'}), 500

@app.route('/api/templates/<int:tpl_id>', methods=['DELETE'])
@jwt_required()
def delete_template(tpl_id):
    user = get_current_user()
    tpl = Template.query.get_or_404(tpl_id)

    if tpl.owner_id != user.id:
        return jsonify({'message': '无权限删除该模板'}), 403

    try:
        db.session.delete(tpl)
        db.session.commit()
        return jsonify({'message': '模板已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '删除模板失败'}), 500

@app.route('/api/patients/<int:patient_id>/records/<int:record_id>/save_as_template', methods=['POST'])
@jwt_required()
def save_record_as_template(patient_id, record_id):
    user = get_current_user()
    Patient.query.get_or_404(patient_id)
    rec = MedicalRecord.query.get_or_404(record_id)

    data = request.get_json() or {}
    tpl_name = data.get('name') or f"模板 - {rec.id} - {rec.record_date.strftime('%Y%m%d')}"
    tpl_desc = data.get('description', '')

    content = {
        'diagnosis': rec.diagnosis,
        'treatment_plan': rec.treatment_plan
    }

    tpl = Template(
        name=tpl_name,
        description=tpl_desc,
        content=json.dumps(content),
        owner_id=user.id
    )

    try:
        db.session.add(tpl)
        db.session.commit()
        return jsonify(tpl.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '保存模板失败'}), 500

@app.route('/api/patients/<int:patient_id>/records/from_template/<int:tpl_id>', methods=['POST'])
@jwt_required()
def create_record_from_template(patient_id, tpl_id):
    Patient.query.get_or_404(patient_id)
    tpl = Template.query.get_or_404(tpl_id)

    try:
        content = json.loads(tpl.content)
    except Exception:
        return jsonify({'message': '模板内容格式错误'}), 400

    payload = request.get_json() or {}
    diagnosis = payload.get('diagnosis', content.get('diagnosis'))
    treatment_plan = payload.get('treatment_plan', content.get('treatment_plan'))

    if not diagnosis or not treatment_plan:
        return jsonify({'message': '创建病历需要诊断和治疗方案'}), 400

    new_record = MedicalRecord(
        diagnosis=diagnosis,
        treatment_plan=treatment_plan,
        patient_id=patient_id
    )

    try:
        db.session.add(new_record)
        db.session.commit()
        return jsonify(new_record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '创建病历失败'}), 500

# 新增：获取科室统计信息的接口
@app.route('/api/departments/stats', methods=['GET'])
@jwt_required()
def get_department_stats():
    """获取各科室的病人统计信息"""
    try:
        stats = db.session.query(
            Patient.department,
            func.count(Patient.id).label('patient_count')
        ).group_by(Patient.department).all()

        result = {}
        for dept, count in stats:
            result[dept] = count

        # 确保所有科室都有数据，即使是0
        departments = ['内科', '外科', '妇产科', '儿科']
        for dept in departments:
            if dept not in result:
                result[dept] = 0

        return jsonify(result)
    except Exception as e:
        return jsonify({'message': '获取统计信息失败'}), 500

# --- 启动命令 ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)