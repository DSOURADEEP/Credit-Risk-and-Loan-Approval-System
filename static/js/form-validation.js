// Form validation utilities

class FormValidator {
    constructor() {
        this.rules = {
            required: (value) => value.trim() !== '',
            min: (value, min) => parseFloat(value) >= min,
            max: (value, max) => parseFloat(value) <= max,
            minLength: (value, length) => value.length >= length,
            maxLength: (value, length) => value.length <= length,
            email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            phone: (value) => /^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$/.test(value),
            creditScore: (value) => {
                const score = parseInt(value);
                return score >= 300 && score <= 850;
            },
            positiveNumber: (value) => parseFloat(value) > 0,
            age: (value) => {
                const age = parseInt(value);
                return age >= 18 && age <= 100;
            },
            salaryConsistency: (salary, monthlyIncome) => {
                const expectedMonthly = salary / 12;
                const variance = Math.abs(monthlyIncome - expectedMonthly) / expectedMonthly;
                return variance <= 0.2; // Allow 20% variance
            }
        };

        this.messages = {
            required: 'This field is required',
            min: 'Value must be at least {min}',
            max: 'Value must be no more than {max}',
            minLength: 'Must be at least {length} characters',
            maxLength: 'Must be no more than {length} characters',
            email: 'Please enter a valid email address',
            phone: 'Please enter a valid phone number',
            creditScore: 'Credit score must be between 300 and 850',
            positiveNumber: 'Value must be greater than 0',
            age: 'Age must be between 18 and 100',
            salaryConsistency: 'Monthly income should be consistent with annual salary'
        };
    }

    validateField(input, rules = []) {
        const value = input.value.trim();
        const errors = [];

        for (const rule of rules) {
            if (typeof rule === 'string') {
                // Simple rule name
                if (!this.rules[rule](value)) {
                    errors.push(this.messages[rule]);
                }
            } else if (typeof rule === 'object') {
                // Rule with parameters
                const { name, params } = rule;
                if (!this.rules[name](value, ...params)) {
                    let message = this.messages[name];
                    // Replace placeholders in message
                    if (params) {
                        params.forEach((param, index) => {
                            const placeholder = Object.keys(rule).find(key => key !== 'name')[index] || `param${index}`;
                            message = message.replace(`{${placeholder}}`, param);
                        });
                    }
                    errors.push(message);
                }
            }
        }

        return errors;
    }

    validateForm(form, validationRules) {
        let isValid = true;
        const errors = {};

        // Validate individual fields
        for (const [fieldName, rules] of Object.entries(validationRules)) {
            const input = form.querySelector(`[name="${fieldName}"]`);
            if (input) {
                const fieldErrors = this.validateField(input, rules);
                if (fieldErrors.length > 0) {
                    errors[fieldName] = fieldErrors;
                    isValid = false;
                    this.showFieldError(input, fieldErrors[0]);
                } else {
                    this.clearFieldError(input);
                }
            }
        }

        // Custom cross-field validation
        this.validateCrossFields(form, errors);

        return { isValid, errors };
    }

    validateCrossFields(form, errors) {
        // Salary vs Monthly Income consistency
        const salaryInput = form.querySelector('[name="customer_salary"]');
        const monthlyIncomeInput = form.querySelector('[name="monthly_income"]');

        if (salaryInput && monthlyIncomeInput) {
            const salary = parseFloat(salaryInput.value) || 0;
            const monthlyIncome = parseFloat(monthlyIncomeInput.value) || 0;

            if (salary > 0 && monthlyIncome > 0) {
                if (!this.rules.salaryConsistency(salary, monthlyIncome)) {
                    errors.monthly_income = errors.monthly_income || [];
                    errors.monthly_income.push(this.messages.salaryConsistency);
                    this.showFieldError(monthlyIncomeInput, this.messages.salaryConsistency);
                }
            }
        }
    }

    showFieldError(input, message) {
        input.classList.add('error');
        input.classList.remove('success');

        const errorElement = document.getElementById(`${input.name}-error`);
        if (errorElement) {
            errorElement.textContent = message;
        }

        // Add shake animation
        input.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => {
            input.style.animation = '';
        }, 500);
    }

    clearFieldError(input) {
        input.classList.remove('error');
        input.classList.add('success');

        const errorElement = document.getElementById(`${input.name}-error`);
        if (errorElement) {
            errorElement.textContent = '';
        }
    }

    setupRealTimeValidation(form, validationRules) {
        for (const [fieldName, rules] of Object.entries(validationRules)) {
            const input = form.querySelector(`[name="${fieldName}"]`);
            if (input) {
                // Validate on blur
                input.addEventListener('blur', () => {
                    const errors = this.validateField(input, rules);
                    if (errors.length > 0) {
                        this.showFieldError(input, errors[0]);
                    } else {
                        this.clearFieldError(input);
                    }
                });

                // Clear errors on input (but don't validate until blur)
                input.addEventListener('input', () => {
                    if (input.classList.contains('error')) {
                        input.classList.remove('error');
                        const errorElement = document.getElementById(`${input.name}-error`);
                        if (errorElement) {
                            errorElement.textContent = '';
                        }
                    }
                });
            }
        }
    }
}

// Loan application specific validation rules
const loanValidationRules = {
    customer_name: ['required', { name: 'minLength', params: [2] }],
    customer_age: ['required', 'age'],
    customer_salary: ['required', 'positiveNumber', { name: 'min', params: [10000] }],
    customer_credit_score: ['required', 'creditScore'],
    loan_amount: ['required', 'positiveNumber', { name: 'min', params: [1000] }, { name: 'max', params: [2000000] }],
    existing_loans: [{ name: 'min', params: [0] }, { name: 'max', params: [20] }],
    monthly_income: ['required', 'positiveNumber'],
    employment_years: ['required', { name: 'min', params: [0] }, { name: 'max', params: [50] }]
};

// Add CSS for shake animation
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Export for use in main app
window.FormValidator = FormValidator;
window.loanValidationRules = loanValidationRules;