// Main application JavaScript

class LoanApplication {
    constructor() {
        this.currentPage = 'application';
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupFormHandlers();
        this.setupEventListeners();

        // Auto-calculate monthly income when salary changes
        this.setupSalaryCalculation();

        console.log('Loan Application System initialized');
    }

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const pages = document.querySelectorAll('.page');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetPage = link.getAttribute('data-page');
                this.showPage(targetPage);
            });
        });
    }

    showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Show target page
        const targetPage = document.getElementById(`${pageId}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        const activeLink = document.querySelector(`[data-page="${pageId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        this.currentPage = pageId;
    }

    setupFormHandlers() {
        const form = document.getElementById('loan-application-form');
        const resetBtn = document.getElementById('reset-form');

        if (form) {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', this.resetForm.bind(this));
        }
    }

    setupEventListeners() {
        // Search history button
        const searchBtn = document.getElementById('search-history');
        if (searchBtn) {
            searchBtn.addEventListener('click', this.searchHistory.bind(this));
        }

        // Enter key in customer ID search
        const customerIdInput = document.getElementById('customer-id-search');
        if (customerIdInput) {
            customerIdInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchHistory();
                }
            });
        }
    }

    setupSalaryCalculation() {
        const salaryInput = document.getElementById('customer_salary');
        const monthlyIncomeInput = document.getElementById('monthly_income');

        if (salaryInput && monthlyIncomeInput) {
            salaryInput.addEventListener('input', () => {
                const salary = parseFloat(salaryInput.value) || 0;
                const monthlyIncome = salary / 12;
                monthlyIncomeInput.value = monthlyIncome.toFixed(2);
            });
        }

        // Enhance tenure dropdown functionality
        this.setupTenureDropdown();
    }

    setupTenureDropdown() {
        const tenureSelect = document.getElementById('preferred_tenure_years');
        
        if (tenureSelect) {
            // Ensure dropdown is properly initialized
            tenureSelect.addEventListener('focus', () => {
                tenureSelect.style.zIndex = '1000';
            });

            tenureSelect.addEventListener('blur', () => {
                tenureSelect.style.zIndex = 'auto';
            });

            // Add change event listener for better UX
            tenureSelect.addEventListener('change', (e) => {
                const selectedValue = e.target.value;
                if (selectedValue) {
                    console.log(`Tenure selected: ${selectedValue} years`);
                    // Add visual feedback
                    e.target.style.borderColor = 'var(--success-color)';
                    setTimeout(() => {
                        e.target.style.borderColor = 'var(--border-color)';
                    }, 1000);
                }
            });

            // Ensure proper styling is applied
            tenureSelect.classList.add('form-input');
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-application');
        const form = e.target;

        try {
            // Show loading state
            this.setLoadingState(submitBtn, true);

            // Validate form
            if (!this.validateForm(form)) {
                this.setLoadingState(submitBtn, false);
                return;
            }

            // Collect form data
            const formData = new FormData(form);
            const applicationData = {
                customer_name: formData.get('customer_name'),
                customer_age: parseInt(formData.get('customer_age')),
                customer_salary: parseFloat(formData.get('customer_salary')),
                customer_credit_score: parseInt(formData.get('customer_credit_score')),
                loan_amount: parseFloat(formData.get('loan_amount')),
                existing_loans: parseInt(formData.get('existing_loans')) || 0,
                monthly_income: parseFloat(formData.get('monthly_income')),
                employment_years: parseFloat(formData.get('employment_years')),
                preferred_tenure_years: formData.get('preferred_tenure_years') ? parseInt(formData.get('preferred_tenure_years')) : null
            };

            // Submit application
            const response = await fetch('/api/v1/loans/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(applicationData)
            });

            let result;
            try {
                result = await response.json();
            } catch (parseError) {
                console.error('Error parsing response:', parseError);
                this.showError('Server returned invalid response. Please try again.');
                return;
            }

            if (response.ok) {
                // Success - show results
                this.displayResults(result);
                this.showPage('results');
                this.resetForm();
            } else {
                // Error - show error message
                console.error('Server error response:', result);
                let errorMessage = 'An error occurred while processing your application';

                if (typeof result === 'string') {
                    errorMessage = result;
                } else if (result && typeof result === 'object') {
                    if (result.detail) {
                        if (typeof result.detail === 'string') {
                            errorMessage = result.detail;
                        } else if (Array.isArray(result.detail)) {
                            errorMessage = result.detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
                        } else {
                            errorMessage = JSON.stringify(result.detail);
                        }
                    } else if (result.message) {
                        errorMessage = result.message;
                    } else if (result.error) {
                        errorMessage = result.error;
                    }
                }

                this.showError(errorMessage);
            }

        } catch (error) {
            console.error('Error submitting application:', error);
            let errorMessage = 'Network error. Please check your connection and try again.';
            if (error.message) {
                errorMessage = error.message;
            }
            this.showError(errorMessage);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required]');

        inputs.forEach(input => {
            const value = input.value.trim();
            const errorElement = document.getElementById(`${input.name}-error`);

            if (!value) {
                this.showFieldError(input, errorElement, 'This field is required');
                isValid = false;
            } else if (input.type === 'number') {
                const numValue = parseFloat(value);
                const min = parseFloat(input.min);
                const max = parseFloat(input.max);

                if (isNaN(numValue)) {
                    this.showFieldError(input, errorElement, 'Please enter a valid number');
                    isValid = false;
                } else if (min !== undefined && numValue < min) {
                    this.showFieldError(input, errorElement, `Value must be at least ${min}`);
                    isValid = false;
                } else if (max !== undefined && numValue > max) {
                    this.showFieldError(input, errorElement, `Value must be no more than ${max}`);
                    isValid = false;
                } else {
                    this.clearFieldError(input, errorElement);
                }
            } else {
                this.clearFieldError(input, errorElement);
            }
        });

        // Additional validation for salary vs monthly income consistency
        const salary = parseFloat(form.customer_salary.value) || 0;
        const monthlyIncome = parseFloat(form.monthly_income.value) || 0;
        const expectedMonthly = salary / 12;
        const variance = Math.abs(monthlyIncome - expectedMonthly) / expectedMonthly;

        if (variance > 0.2) { // Allow 20% variance
            const monthlyError = document.getElementById('monthly_income-error');
            this.showFieldError(form.monthly_income, monthlyError, 'Monthly income should be consistent with annual salary');
            isValid = false;
        }

        return isValid;
    }

    showFieldError(input, errorElement, message) {
        input.classList.add('error');
        if (errorElement) {
            errorElement.textContent = message;
        }
    }

    clearFieldError(input, errorElement) {
        input.classList.remove('error');
        if (errorElement) {
            errorElement.textContent = '';
        }
    }

    setLoadingState(button, loading) {
        if (loading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }

    resetForm() {
        const form = document.getElementById('loan-application-form');
        if (form) {
            form.reset();

            // Clear all error messages
            const errorElements = form.querySelectorAll('.error-message');
            errorElements.forEach(element => {
                element.textContent = '';
            });

            // Remove error classes
            const inputs = form.querySelectorAll('.form-input');
            inputs.forEach(input => {
                input.classList.remove('error', 'success');
            });
        }
    }

    displayResults(result) {
        const resultsContent = document.getElementById('results-content');
        if (!resultsContent) return;

        const statusClass = `status-${result.status}`;
        const riskClass = result.risk_category ? `risk-${result.risk_category}` : '';

        let html = `
            <div class="result-card">
                <div class="result-header">
                    <h3 class="result-title">Application #${result.application_id}</h3>
                    <span class="status-badge ${statusClass}">${result.status.replace('_', ' ')}</span>
                </div>
                
                <div class="result-details">
                    <div class="detail-item">
                        <span class="detail-label">Customer ID</span>
                        <span class="detail-value">${result.customer_id}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Processing Time</span>
                        <span class="detail-value">${result.processing_time_ms}ms</span>
                    </div>
                    ${result.risk_category ? `
                    <div class="detail-item">
                        <span class="detail-label">Risk Category</span>
                        <span class="detail-value">
                            <span class="risk-badge ${riskClass}">${result.risk_category}</span>
                        </span>
                    </div>
                    ` : ''}
                </div>

                <div class="detail-item" style="margin-top: 1rem;">
                    <span class="detail-label">Decision Reason</span>
                    <span class="detail-value">${result.decision_reason}</span>
                </div>
            </div>
        `;

        // Add loan terms if approved
        if (result.loan_terms) {
            html += `
                <div class="loan-terms">
                    <h4 class="loan-terms-title">Approved Loan Terms</h4>
                    <div class="terms-grid">
                        <div class="detail-item">
                            <span class="detail-label">Approved Amount</span>
                            <span class="detail-value">Rs. ${result.loan_terms.approved_amount.toLocaleString('en-IN')}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Interest Rate</span>
                            <span class="detail-value">${result.loan_terms.interest_rate}% per annum</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Tenure</span>
                            <span class="detail-value">${result.loan_terms.tenure_months} months (${(result.loan_terms.tenure_months / 12).toFixed(1)} years)</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Monthly Payment</span>
                            <span class="detail-value">Rs. ${result.loan_terms.monthly_payment.toLocaleString('en-IN')}</span>
                        </div>
                    </div>
                </div>
            `;
        }

        // Add ML evaluation info if available
        if (result.ml_evaluation) {
            html += `
                <div class="result-card" style="margin-top: 1rem;">
                    <h4 class="result-title">ML Model Evaluation</h4>
                    <div class="result-details">
                        <div class="detail-item">
                            <span class="detail-label">ML Decision</span>
                            <span class="detail-value">${result.ml_evaluation.final_decision}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Model Consensus</span>
                            <span class="detail-value">${result.ml_evaluation.consensus ? 'Yes' : 'No'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Confidence</span>
                            <span class="detail-value">${(result.ml_evaluation.average_probability * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
            `;
        }

        resultsContent.innerHTML = html;
    }

    async searchHistory() {
        const customerIdInput = document.getElementById('customer-id-search');
        const historyContent = document.getElementById('history-content');

        if (!customerIdInput || !historyContent) return;

        const customerId = customerIdInput.value.trim();
        if (!customerId) {
            this.showError('Please enter a customer ID');
            return;
        }

        try {
            historyContent.innerHTML = '<div class="loading">Loading loan history...</div>';

            const response = await fetch(`/api/v1/customers/${customerId}/history`);
            const history = await response.json();

            if (response.ok) {
                this.displayHistory(history);
            } else {
                historyContent.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📋</div>
                        <p>No loan history found for customer ID ${customerId}</p>
                    </div>
                `;
            }

        } catch (error) {
            console.error('Error fetching history:', error);
            historyContent.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>Error loading loan history. Please try again.</p>
                </div>
            `;
        }
    }

    displayHistory(history) {
        const historyContent = document.getElementById('history-content');
        if (!historyContent) return;

        if (!history || history.length === 0) {
            historyContent.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <p>No loan applications found</p>
                </div>
            `;
            return;
        }

        let html = `
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Application ID</th>
                        <th>Date</th>
                        <th>Loan Amount</th>
                        <th>Status</th>
                        <th>Risk Category</th>
                        <th>Approved Amount</th>
                    </tr>
                </thead>
                <tbody>
        `;

        history.forEach(app => {
            const date = new Date(app.application_date).toLocaleDateString();
            const statusClass = `status-${app.status}`;
            const riskClass = app.risk_category ? `risk-${app.risk_category}` : '';
            const approvedAmount = app.loan_terms ? `Rs. ${app.loan_terms.approved_amount.toLocaleString('en-IN')}` : '-';

            html += `
                <tr>
                    <td>${app.application_id}</td>
                    <td>${date}</td>
                    <td>Rs. ${app.loan_amount.toLocaleString('en-IN')}</td>
                    <td><span class="status-badge ${statusClass}">${app.status.replace('_', ' ')}</span></td>
                    <td>${app.risk_category ? `<span class="risk-badge ${riskClass}">${app.risk_category}</span>` : '-'}</td>
                    <td>${approvedAmount}</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        historyContent.innerHTML = html;
    }

    showError(message) {
        // Ensure message is a string
        let displayMessage = message;
        if (typeof message !== 'string') {
            displayMessage = JSON.stringify(message);
        }

        console.error('Showing error:', displayMessage);

        // Create or update error display
        let errorDiv = document.getElementById('error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'error-message';
            errorDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: #dc3545;
                color: white;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                z-index: 1000;
                max-width: 400px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;
            document.body.appendChild(errorDiv);
        }

        errorDiv.textContent = displayMessage;
        errorDiv.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LoanApplication();
});