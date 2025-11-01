// Set today's date as default
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
    
    // Load initial data
    loadTransactions();
    loadSummary();
    
    // Setup form submission
    const form = document.getElementById('transaction-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
    
    // Setup currency conversion preview
    const currencySelect = document.getElementById('currency');
    const amountInput = document.getElementById('amount');
    const dateInputForConversion = document.getElementById('date');
    
    if (currencySelect && amountInput) {
        currencySelect.addEventListener('change', updateConversionPreview);
        amountInput.addEventListener('input', updateConversionPreview);
        if (dateInputForConversion) {
            dateInputForConversion.addEventListener('change', updateConversionPreview);
        }
    }
});

// Update conversion preview
let conversionTimeout;
async function updateConversionPreview() {
    clearTimeout(conversionTimeout);
    
    const currencySelect = document.getElementById('currency');
    const amountInput = document.getElementById('amount');
    const dateInput = document.getElementById('date');
    const previewDiv = document.getElementById('conversion-preview');
    const previewText = document.getElementById('conversion-text');
    
    if (!currencySelect || !amountInput || !previewDiv || !previewText) return;
    
    const currency = currencySelect.value;
    const amount = parseFloat(amountInput.value);
    const date = dateInput ? dateInput.value : new Date().toISOString().split('T')[0];
    
    // Don't show preview if amount is empty, zero, or currency is IDR
    if (!amount || amount <= 0 || currency === 'IDR') {
        previewDiv.style.display = 'none';
        return;
    }
    
    // Debounce the API call
    conversionTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/exchange-rate?from=${currency}&to=IDR&date=${date}`);
            const data = await response.json();
            
            if (data.success && data.rate) {
                const convertedAmount = amount * data.rate;
                previewText.textContent = `≈ ${formatCurrency(convertedAmount)} (Rate: 1 ${currency} = ${formatCurrency(data.rate)})`;
                previewDiv.style.display = 'block';
            } else {
                previewDiv.style.display = 'none';
            }
        } catch (error) {
            console.error('Error fetching exchange rate:', error);
            previewDiv.style.display = 'none';
        }
    }, 500); // Wait 500ms after user stops typing
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const transactionData = {
        description: formData.get('description'),
        amount: parseFloat(formData.get('amount')),
        currency: formData.get('currency'),
        transaction_type: formData.get('transaction_type'),
        date: formData.get('date'),
        category: formData.get('category') || ''
    };
    
    try {
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(transactionData)
        });
        
        if (response.ok) {
            // Reset form
            e.target.reset();
            // Set default date again
            const dateInput = document.getElementById('date');
            if (dateInput) {
                const today = new Date().toISOString().split('T')[0];
                dateInput.value = today;
            }
            
            // Reload data
            loadTransactions();
            loadSummary();
        } else {
            alert('Error adding transaction. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding transaction. Please try again.');
    }
}

// Load transactions from API
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();
        
        const transactionsList = document.getElementById('transactions-list');
        if (!transactionsList) return;
        
        if (transactions.length === 0) {
            transactionsList.innerHTML = '<p class="empty-state">No transactions yet. Add your first transaction above!</p>';
            return;
        }
        
        transactionsList.innerHTML = transactions.map(transaction => {
            const originalCurrency = transaction.original_currency || 'IDR';
            const originalAmount = transaction.original_amount;
            const showOriginal = originalCurrency !== 'IDR' && originalAmount;
            
            return `
            <div class="transaction-item ${transaction.transaction_type}">
                <div class="transaction-info">
                    <h4>${escapeHtml(transaction.description)}</h4>
                    <div class="transaction-meta">
                        <span>${formatDate(transaction.date)}</span>
                        ${transaction.category ? `<span>${escapeHtml(transaction.category)}</span>` : ''}
                        ${showOriginal ? `<span style="font-size: 0.85em; color: #888;">
                            (${originalAmount.toLocaleString('id-ID')} ${originalCurrency} @ ${transaction.exchange_rate ? transaction.exchange_rate.toFixed(4) : 'N/A'})
                        </span>` : ''}
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="transaction-amount">
                        ${transaction.transaction_type === 'income' ? '+' : '-'}${formatCurrency(transaction.amount)}
                    </span>
                    <button class="btn btn-danger" onclick="deleteTransaction(${transaction.id})">Delete</button>
                </div>
            </div>
        `;
        }).join('');
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Load summary from API
async function loadSummary() {
    try {
        const response = await fetch('/api/summary');
        const summary = await response.json();
        
        const totalIncomeEl = document.getElementById('total-income');
        const totalExpenseEl = document.getElementById('total-expense');
        const balanceEl = document.getElementById('balance');
        
        if (totalIncomeEl) {
            totalIncomeEl.textContent = formatCurrency(summary.total_income);
        }
        if (totalExpenseEl) {
            totalExpenseEl.textContent = formatCurrency(summary.total_expense);
        }
        if (balanceEl) {
            balanceEl.textContent = formatCurrency(summary.balance);
            // Change color based on balance
            if (summary.balance < 0) {
                balanceEl.style.color = '#dc3545';
            } else {
                balanceEl.style.color = '#007bff';
            }
        }
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Delete transaction
async function deleteTransaction(id) {
    if (!confirm('Are you sure you want to delete this transaction?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/transactions/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadTransactions();
            loadSummary();
        } else {
            alert('Error deleting transaction. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting transaction. Please try again.');
    }
}

// Helper functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function formatCurrency(amount) {
    // Format as Indonesian Rupiah (IDR)
    // IDR typically doesn't use decimal places
    const formattedAmount = Math.round(amount).toLocaleString('id-ID');
    return `Rp ${formattedAmount}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

