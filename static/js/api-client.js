// API client for loan application system

class ApiClient {
    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new ApiError(data, response.status);
            }

            return data;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError({ 
                error: 'NETWORK_ERROR', 
                message: 'Network request failed' 
            }, 0);
        }
    }

    // Loan endpoints
    async submitLoanApplication(applicationData) {
        return this.request('/loans/apply', {
            method: 'POST',
            body: JSON.stringify(applicationData)
        });
    }

    async getLoanDecision(applicationId) {
        return this.request(`/loans/${applicationId}/decision`);
    }

    async getApplicationStatus(applicationId) {
        return this.request(`/loans/status/${applicationId}`);
    }

    // Customer endpoints
    async getCustomerHistory(customerId) {
        return this.request(`/customers/${customerId}/history`);
    }

    async getCustomerProfile(customerId) {
        return this.request(`/customers/${customerId}/profile`);
    }

    async getCustomerSummary(customerId) {
        return this.request(`/customers/${customerId}/summary`);
    }

    // Health endpoints
    async getHealthStatus() {
        return this.request('/health');
    }

    async getDetailedHealthStatus() {
        return this.request('/health/detailed');
    }

    async getDatabaseHealth() {
        return this.request('/health/database');
    }

    async getMlServiceHealth() {
        return this.request('/health/ml');
    }
}

class ApiError extends Error {
    constructor(errorData, statusCode) {
        super(errorData.message || 'API request failed');
        this.name = 'ApiError';
        this.errorData = errorData;
        this.statusCode = statusCode;
    }

    getErrorMessage() {
        if (this.errorData.details) {
            if (Array.isArray(this.errorData.details)) {
                // Validation errors
                return this.errorData.details
                    .map(detail => `${detail.field}: ${detail.message}`)
                    .join(', ');
            } else if (typeof this.errorData.details === 'object') {
                // Business rule errors
                return this.errorData.details.message || this.message;
            }
        }
        return this.message;
    }

    isValidationError() {
        return this.errorData.error === 'VALIDATION_ERROR';
    }

    isBusinessRuleError() {
        return this.errorData.error === 'BUSINESS_RULE_ERROR';
    }

    isNetworkError() {
        return this.statusCode === 0;
    }
}

// Utility functions for common API operations
class LoanApiHelper {
    constructor() {
        this.api = new ApiClient();
    }

    async submitApplication(formData) {
        try {
            const result = await this.api.submitLoanApplication(formData);
            return { success: true, data: result };
        } catch (error) {
            return { 
                success: false, 
                error: error.getErrorMessage(),
                isValidationError: error.isValidationError(),
                isBusinessRuleError: error.isBusinessRuleError()
            };
        }
    }

    async checkApplicationStatus(applicationId) {
        try {
            const result = await this.api.getApplicationStatus(applicationId);
            return { success: true, data: result };
        } catch (error) {
            return { 
                success: false, 
                error: error.getErrorMessage()
            };
        }
    }

    async getCustomerLoanHistory(customerId) {
        try {
            const result = await this.api.getCustomerHistory(customerId);
            return { success: true, data: result };
        } catch (error) {
            return { 
                success: false, 
                error: error.getErrorMessage()
            };
        }
    }

    async checkSystemHealth() {
        try {
            const result = await this.api.getDetailedHealthStatus();
            return { success: true, data: result };
        } catch (error) {
            return { 
                success: false, 
                error: error.getErrorMessage()
            };
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    formatPercentage(value) {
        return `${(value * 100).toFixed(2)}%`;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    getStatusColor(status) {
        const colors = {
            'approved': '#10b981',
            'rejected': '#ef4444',
            'pending': '#f59e0b',
            'manual_review': '#6366f1'
        };
        return colors[status] || '#64748b';
    }

    getRiskColor(riskCategory) {
        const colors = {
            'low': '#10b981',
            'medium': '#f59e0b',
            'high': '#ef4444'
        };
        return colors[riskCategory] || '#64748b';
    }
}

// Request interceptor for adding authentication if needed
class AuthenticatedApiClient extends ApiClient {
    constructor(baseUrl) {
        super(baseUrl);
        this.token = localStorage.getItem('authToken');
    }

    setAuthToken(token) {
        this.token = token;
        localStorage.setItem('authToken', token);
    }

    clearAuthToken() {
        this.token = null;
        localStorage.removeItem('authToken');
    }

    async request(endpoint, options = {}) {
        if (this.token) {
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${this.token}`
            };
        }

        try {
            return await super.request(endpoint, options);
        } catch (error) {
            if (error.statusCode === 401) {
                // Token expired or invalid
                this.clearAuthToken();
                // Could redirect to login page here
            }
            throw error;
        }
    }
}

// Export classes for use in other modules
window.ApiClient = ApiClient;
window.ApiError = ApiError;
window.LoanApiHelper = LoanApiHelper;
window.AuthenticatedApiClient = AuthenticatedApiClient;