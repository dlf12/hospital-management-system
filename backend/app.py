# 从 flask 库中导入 Flask 类（用来创建服务器）、request 对象（用来接收前端数据）、jsonify 函数（用来创建 JSON 格式的响应）
from flask import Flask, request, jsonify

# 从 flask_sqlalchemy 库中导入 SQLAlchemy 类（用来操作数据库）
from flask_sqlalchemy import SQLAlchemy

# 从 flask_cors 库中导入 CORS 类（用来解决跨域问题）
from flask_cors import CORS





# 1. 创建一个 Flask 应用实例，这就是我们的服务器主体
app = Flask(__name__)

# 2. 允许所有来源的跨域请求
CORS(app)

# 3. 配置数据库的连接地址
#    格式是: 'mysql+pymysql://用户名:你的密码@服务器地址/数据库名'
#    请务必把 your_password 替换成你自己的 MySQL root 密码！
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1/hospital_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 4. 创建数据库操作对象，并与我们的 Flask 应用关联起来
db = SQLAlchemy(app)




# -- 数据模型定义 --
# 这个类对应数据库里的 'patients' 表
class Patient(db.Model):
    __tablename__ = 'patients'  # 明确指定表名
    # 定义表中的每一个字段/列
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    id_card = db.Column(db.String(18), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))

    # 这是一个辅助函数，方便我们之后把查询结果转换成前端需要的 JSON 格式
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# 这个类对应数据库里的 'users' 表
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)






    # --- API 接口定义 ---

# 获取所有病人的接口
@app.route('/api/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([patient.to_dict() for patient in patients])

# 新增一个病人的接口
@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    new_patient = Patient(name=data['name'], id_card=data['id_card'], age=data['age'], gender=data['gender'])
    db.session.add(new_patient)
    db.session.commit()
    return jsonify(new_patient.to_dict()), 201

# 删除一个病人的接口
@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'})

# 用户登录的接口
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
# 这是一个 Python 的标准写法，意思是：
# 只有当这个 app.py 文件被直接运行时，才执行下面的 app.run()
if __name__ == '__main__':
    # 启动 Flask web 服务器
    # debug=True 表示开启调试模式，这样当你修改代码并保存后，服务器会自动重启
    app.run(debug=True)