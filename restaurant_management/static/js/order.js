// Add this to your existing orders.html script section
const API_ENDPOINTS = {
    MENU_ITEMS: '/api/menu-items/',
    ORDERS: '/api/orders/',
    CREATE_ORDER: '/api/create-order/',
    UPDATE_ORDER_STATUS: '/api/update-order-status/'
};

// Replace the static data with API calls
async function fetchOrders() {
    try {
        const response = await fetch(API_ENDPOINTS.ORDERS);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching orders:', error);
        return [];
    }
}

async function fetchMenuItems() {
    try {
        const response = await fetch(API_ENDPOINTS.MENU_ITEMS);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching menu items:', error);
        return [];
    }
}

// Update the initialization function
document.addEventListener('DOMContentLoaded', async function() {
    const orders = await fetchOrders();
    const menuItems = await fetchMenuItems();
    populateOrdersTable(orders);
    populateMenuItems(menuItems);
});

// Update the create order function
document.getElementById('createOrderBtn').addEventListener('click', async function() {
    const tableNumber = document.getElementById('tableNumber').value;
    const selectedItems = Array.from(document.getElementById('orderItems').selectedOptions)
        .map(option => ({
            menu_item_id: parseInt(option.value),
            quantity: 1
        }));
    
    if (!tableNumber || selectedItems.length === 0) {
        alert('Please fill in all fields');
        return;
    }

    try {
        const response = await fetch(API_ENDPOINTS.CREATE_ORDER, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                table_number: parseInt(tableNumber),
                items: selectedItems
            })
        });

        if (response.ok) {
            const orders = await fetchOrders();
            populateOrdersTable(orders);
            closeNewOrderModal();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to create order');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        alert('Failed to create order');
    }
});

// Add CSRF token helper function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Update the status update function
async function updateOrderStatus(orderId) {
    const order = orders.find(o => o.id === orderId);
    if (!order) return;

    const statusFlow = {
        'pending': 'preparing',
        'preparing': 'ready',
        'ready': 'completed',
        'completed': 'completed'
    };

    const newStatus = statusFlow[order.status];

    try {
        const response = await fetch(`${API_ENDPOINTS.UPDATE_ORDER_STATUS}${orderId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                status: newStatus
            })
        });

        if (response.ok) {
            const orders = await fetchOrders();
            populateOrdersTable(orders);
        } else {
            alert('Failed to update order status');
        }
    } catch (error) {
        console.error('Error updating order status:', error);
        alert('Failed to update order status');
    }
}