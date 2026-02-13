const API_BASE_URL = import.meta.env.PROD
    ? "https://wiki-quiz-backend-q0vk.onrender.com/api/quiz"
    : "http://localhost:8000/api/quiz";

export default API_BASE_URL;
