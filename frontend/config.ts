const getBackendUrl = () => {
    return process.env.BACKEND_URI || 'http://127.0.0.1:8000';
};

export const BACKEND_URI = getBackendUrl();