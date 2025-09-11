# 从 flask 库中导入 Flask 类、request 对象、jsonify 函数
from flask import Flask, request, jsonify
# 从 flask_sqlalchemy 库中导入 SQLAlchemy 类
from flask_sqlalchemy import SQLAlchemy
# 从 flask_cors 库中导入 CORS 类
from flask_cors import CORS
# 导入 datetime 用于记录病历时间
from datetime import datetime

# 1. 创建 Flask 应用实例
app = Flask(__name__)

# 2. 允许跨域请求
CORS(app)

# 3. 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1/hospital_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 4. 创建数据库操作对象
db = SQLAlchemy(app)


# --- 数据模型定义 ---

# 病人模型 (Patient Model)
class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    id_card = db.Column(db.String(18), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    # 新增：建立与病历的一对多关系
    # backref='patient' 允许我们通过一个 MedicalRecord 对象用 record.patient 访问其关联的 Patient 对象
    # lazy=True 表示在需要时才加载关联的病历
    records = db.relationship('MedicalRecord', backref='patient', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# 新增：病历模型 (MedicalRecord Model)
class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.Text, nullable=False)      # 诊断信息
    treatment_plan = db.Column(db.Text, nullable=False) # 治疗方案
    record_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # 记录日期
    # 新增：外键，关联到病人表的 id 字段
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    def to_dict(self):
        # 转换时也包含日期的字符串格式
        return {
            'id': self.id,
            'diagnosis': self.diagnosis,
            'treatment_plan': self.treatment_plan,
            'record_date': self.record_date.strftime('%Y-%m-%d %H:%M:%S'), # 格式化日期
            'patient_id': self.patient_id
        }

# 用户模型 (User Model)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# --- API 接口定义 ---

# -- 病人接口 --
@app.route('/api/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([patient.to_dict() for patient in patients])

@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    new_patient = Patient(name=data['name'], id_card=data['id_card'], age=data['age'], gender=data['gender'])
    db.session.add(new_patient)
    db.session.commit()
    return jsonify(new_patient.to_dict()), 201

@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'})

# -- 新增：病历接口 --

# 获取指定病人的所有病历
@app.route('/api/patients/<int:patient_id>/records', methods=['GET'])
def get_records_for_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.record_date.desc()).all()
    return jsonify([record.to_dict() for record in records])

# 为指定病人新增一条病历
@app.route('/api/patients/<int:patient_id>/records', methods=['POST'])
def add_record_for_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()

    if not data or not data.get('diagnosis') or not data.get('treatment_plan'):
        return jsonify({'message': '诊断信息和治疗方案不能为空'}), 400

    new_record = MedicalRecord(
        diagnosis=data['diagnosis'],
        treatment_plan=data['treatment_plan'],
        patient_id=patient.id
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify(new_record.to_dict()), 201


# -- 用户登录接口 --
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '用户名和密码不能为空'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        return jsonify({'message': '登录成功'}), 200
    else:
        return jsonify({'message': '用户名或密码错误'}), 401


# --- 启动命令 ---
if __name__ == '__main__':
    # 在第一次运行前，需要初始化数据库
    with app.app_context():
        db.create_all()
    app.run(debug=True)