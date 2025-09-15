import axios from 'axios';

// 1. 创建 Axios 实例
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:5000/api', // 设置统一的 API 基础路径
    headers: {
        'Content-Type': 'application/json',
    },
});

// 2. 添加请求拦截器 (Request Interceptor)
//    这个函数会在每次发送请求之前被调用
apiClient.interceptors.request.use(
    (config) => {
        // 从 localStorage 获取 token
        const token = localStorage.getItem('accessToken');

        // 如果 token 存在，则将其添加到请求的 Authorization 头中
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        return config; // 返回修改后的配置
    },
    (error) => {
        // 处理请求错误
        return Promise.reject(error);
    }
);

// 3. 导出配置好的 Axios 实例
export default apiClient;