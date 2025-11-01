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
});

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const transactionData = {
        description: formData.get('description'),
        amount: parseFloat(formData.get('amount')),
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
        
        transactionsList.innerHTML = transactions.map(transaction => `
            <div class="transaction-item ${transaction.transaction_type}">
                <div class="transaction-info">
                    <h4>${escapeHtml(transaction.description)}</h4>
                    <div class="transaction-meta">
                        <span>${formatDate(transaction.date)}</span>
                        ${transaction.category ? `<span>${escapeHtml(transaction.category)}</span>` : ''}
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="transaction-amount">
                        ${transaction.transaction_type === 'income' ? '+' : '-'}$${transaction.amount.toFixed(2)}
                    </span>
                    <button class="btn btn-danger" onclick="deleteTransaction(${transaction.id})">Delete</button>
                </div>
            </div>
        `).join('');
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
            totalIncomeEl.textContent = `$${summary.total_income.toFixed(2)}`;
        }
        if (totalExpenseEl) {
            totalExpenseEl.textContent = `$${summary.total_expense.toFixed(2)}`;
        }
        if (balanceEl) {
            balanceEl.textContent = `$${summary.balance.toFixed(2)}`;
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

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

