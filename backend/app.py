# --- 导入必要的库 ---
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate  # 新增：数据库迁移
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity # 新增：JWT认证
from werkzeug.security import generate_password_hash, check_password_hash # 新增：密码哈希
from datetime import datetime
from sqlalchemy import or_ # 新增：用于实现搜索功能


from sqlalchemy import func
from flask_jwt_extended import get_jwt_identity
import json


# 1. 创建 Flask 应用实例
app = Flask(__name__)

# 2. 允许跨域请求
CORS(app)

# 3. 配置
# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1/hospital_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 新增：JWT 密钥配置，用于加密Token，请务必修改为一个复杂的随机字符串
app.config["JWT_SECRET_KEY"] = "1943860229"

# 4. 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # 初始化 Flask-Migrate
jwt = JWTManager(app)       # 初始化 JWTManager

# --- 数据模型定义 ---

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # 修改：不再存储明文密码

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
    phone_number = db.Column(db.String(20)) # 新增：联系电话字段

    records = db.relationship('MedicalRecord', backref='patient', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

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
    name = db.Column(db.String(255), nullable=False)            # 模板名
    description = db.Column(db.Text, nullable=True)             # 描述/备注
    content = db.Column(db.Text, nullable=False)                # 存 JSON 或直接文本（例如包含 diagnosis/treatment_plan）
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_shared = db.Column(db.Boolean, default=False)            # 是否对同机构/所有用户共享（简单设计）
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    owner = db.relationship('User', backref='templates')

    def to_dict(self):
        # 尝试把 content 解析为 JSON，否则返回原始字符串
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
        # 登录成功，生成JWT Token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

    return jsonify({"message": "用户名或密码错误"}), 401

# -- 病人接口 (受保护) --
@app.route('/api/patients', methods=['GET'])
@jwt_required()  # 保持原有保护
def get_patients():
    # 搜索
    search_query = request.args.get('search', '').strip()
    # 分页参数（默认 page=1, per_page=20）
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    try:
        per_page = min(100, max(1, int(request.args.get('per_page', 20))))
    except ValueError:
        per_page = 20

    query = Patient.query
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(or_(Patient.name.like(search_term), Patient.id_card.like(search_term)))

    # 使用 SQLAlchemy 的 paginate（Flask-SQLAlchemy >=2.5 支持）
    pagination = query.order_by(Patient.name).paginate(page=page, per_page=per_page, error_out=False)

    items = [patient.to_dict() for patient in pagination.items]
    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page
    })


@app.route('/api/patients', methods=['POST'])
@jwt_required() # 添加保护
def add_patient():
    data = request.get_json()
    if Patient.query.filter_by(id_card=data['id_card']).first():
        return jsonify({'message': '该身份证号已存在'}), 409

    new_patient = Patient(
        name=data['name'],
        id_card=data['id_card'],
        age=data.get('age'),
        gender=data.get('gender'),
        phone_number=data.get('phone_number')
    )
    db.session.add(new_patient)
    db.session.commit()
    return jsonify(new_patient.to_dict()), 201

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
@jwt_required() # 添加保护
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    patient.name = data.get('name', patient.name)
    patient.id_card = data.get('id_card', patient.id_card)
    patient.age = data.get('age', patient.age)
    patient.gender = data.get('gender', patient.gender)
    patient.phone_number = data.get('phone_number', patient.phone_number)
    db.session.commit()
    return jsonify(patient.to_dict())


@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
@jwt_required() # 添加保护
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'})

# -- 病历接口 (受保护) --
@app.route('/api/patients/<int:patient_id>/records', methods=['GET'])
@jwt_required() # 添加保护
def get_records_for_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.record_date.desc()).all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/patients/<int:patient_id>/records', methods=['POST'])
@jwt_required() # 添加保护
def add_record_for_patient(patient_id):
    Patient.query.get_or_404(patient_id) # 确保病人存在
    data = request.get_json()
    if not data or not data.get('diagnosis') or not data.get('treatment_plan'):
        return jsonify({'message': '诊断信息和治疗方案不能为空'}), 400
    new_record = MedicalRecord(
        diagnosis=data['diagnosis'],
        treatment_plan=data['treatment_plan'],
        patient_id=patient_id
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify(new_record.to_dict()), 201



@app.route('/api/templates', methods=['GET'])
@jwt_required()
def list_templates():
    user = get_current_user()
    # 支持查询共享模板与自己模板
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
    db.session.add(tpl)
    db.session.commit()
    return jsonify(tpl.to_dict()), 201


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
    db.session.commit()
    return jsonify(tpl.to_dict())

@app.route('/api/templates/<int:tpl_id>', methods=['DELETE'])
@jwt_required()
def delete_template(tpl_id):
    user = get_current_user()
    tpl = Template.query.get_or_404(tpl_id)
    if tpl.owner_id != user.id:
        return jsonify({'message': '无权限删除该模板'}), 403
    db.session.delete(tpl)
    db.session.commit()
    return jsonify({'message': '模板已删除'})


@app.route('/api/patients/<int:patient_id>/records/<int:record_id>/save_as_template', methods=['POST'])
@jwt_required()
def save_record_as_template(patient_id, record_id):
    user = get_current_user()
    # 验证病人和病历存在
    Patient.query.get_or_404(patient_id)
    rec = MedicalRecord.query.get_or_404(record_id)
    # 构建模板内容（可按需扩展：把diagnosis/treatment_plan/其它字段放入content）
    tpl_name = request.get_json().get('name') or f"模板 - {rec.id} - {rec.record_date.strftime('%Y%m%d')}"
    tpl_desc = request.get_json().get('description', '')
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
    db.session.add(tpl)
    db.session.commit()
    return jsonify(tpl.to_dict()), 201


@app.route('/api/patients/<int:patient_id>/records/from_template/<int:tpl_id>', methods=['POST'])
@jwt_required()
def create_record_from_template(patient_id, tpl_id):
    Patient.query.get_or_404(patient_id)
    tpl = Template.query.get_or_404(tpl_id)
    # 解析内容，支持纯文本或 json
    try:
        content = json.loads(tpl.content)
    except Exception:
        # 推测 content 为字符串，前端应提供 diagnosis/treatment_plan
        return jsonify({'message': '模板内容不可解析为 JSON，请前端传递具体字段'}), 400
    # 允许前端覆盖
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
    db.session.add(new_record)
    db.session.commit()
    return jsonify(new_record.to_dict()), 201


# --- 启动命令 ---
if __name__ == '__main__':
    # 注意：db.create_all() 仍在首次运行时有用，但后续的模型变更应使用 Flask-Migrate
    with app.app_context():
        db.create_all()
    app.run(debug=True)