const getBackendUrl = () => {
    return process.env.NEXT_PUBLIC_BACKEND_URI || 'https://backend-api-guideme.azurewebsites.net';
};

export const BACKEND_URI = getBackendUrl();