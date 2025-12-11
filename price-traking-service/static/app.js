// API базовый URL (будет настроен при интеграции с бэкендом)
const API_BASE_URL = 'http://localhost:8000/api';

// Состояние приложения
let alerts = [];
let cryptoPrices = {};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadCryptoPrices();
    loadAlerts();
    
    // Обновление цен каждые 30 секунд
    setInterval(loadCryptoPrices, 30000);
});

// Обработчики событий
function initEventListeners() {
    const form = document.getElementById('createAlertForm');
    form.addEventListener('submit', handleCreateAlert);
    
    const cancelBtn = document.getElementById('cancelDelete');
    const confirmBtn = document.getElementById('confirmDelete');
    
    cancelBtn.addEventListener('click', closeDeleteModal);
    confirmBtn.addEventListener('click', handleDeleteAlert);
}

// Загрузка цен криптовалют
async function loadCryptoPrices() {
    const container = document.getElementById('cryptoPrices');
    
    // Показываем скелетон загрузки
    container.innerHTML = Array(8).fill(0).map(() => 
        '<div class="crypto-card loading"><div class="skeleton"></div></div>'
    ).join('');
    
    try {
        // TODO: Заменить на реальный API вызов
        // const response = await fetch(`${API_BASE_URL}/cryptocurrencies/prices`);
        // const data = await response.json();
        
        // Мок данные для демонстрации
        const mockData = [
            { symbol: 'BTC', name: 'Bitcoin', price: 43250.50, change: 2.5 },
            { symbol: 'ETH', name: 'Ethereum', price: 2650.75, change: -1.2 },
            { symbol: 'BNB', name: 'Binance Coin', price: 315.20, change: 0.8 },
            { symbol: 'SOL', name: 'Solana', price: 98.45, change: 5.3 },
            { symbol: 'ADA', name: 'Cardano', price: 0.52, change: -0.5 },
            { symbol: 'XRP', name: 'Ripple', price: 0.62, change: 1.8 },
            { symbol: 'DOT', name: 'Polkadot', price: 7.25, change: -2.1 },
            { symbol: 'DOGE', name: 'Dogecoin', price: 0.085, change: 3.7 },
        ];
        
        cryptoPrices = {};
        mockData.forEach(crypto => {
            cryptoPrices[crypto.symbol] = crypto;
        });
        
        renderCryptoPrices(mockData);
    } catch (error) {
        console.error('Ошибка загрузки цен:', error);
        showNotification('Ошибка загрузки цен криптовалют', 'error');
    }
}

// Отображение цен
function renderCryptoPrices(data) {
    const container = document.getElementById('cryptoPrices');
    
    if (data.length === 0) {
        container.innerHTML = '<p class="empty-state">Нет данных о ценах</p>';
        return;
    }
    
    container.innerHTML = data.map(crypto => `
        <div class="crypto-card">
            <div class="crypto-header">
                <div class="crypto-symbol">${crypto.symbol}</div>
                <div class="crypto-change ${crypto.change >= 0 ? 'positive' : 'negative'}">
                    ${crypto.change >= 0 ? '↑' : '↓'} ${Math.abs(crypto.change).toFixed(2)}%
                </div>
            </div>
            <div class="crypto-name">${crypto.name}</div>
            <div class="crypto-price">$${formatPrice(crypto.price)}</div>
        </div>
    `).join('');
}

// Форматирование цены
function formatPrice(price) {
    if (price >= 1000) {
        return price.toLocaleString('ru-RU', { maximumFractionDigits: 2 });
    }
    return price.toFixed(price < 1 ? 4 : 2);
}

// Загрузка алертов
async function loadAlerts() {
    try {
        // TODO: Заменить на реальный API вызов
        // const response = await fetch(`${API_BASE_URL}/alerts`);
        // const data = await response.json();
        
        // Мок данные для демонстрации
        const mockAlerts = [
            {
                id: '1',
                email: 'user@example.com',
                cryptocurrency: 'BTC',
                threshold_price: 45000,
                threshold_percent: 5.0,
                condition: 'above',
                is_active: true,
                created_at: '2024-01-15T10:30:00Z'
            },
            {
                id: '2',
                email: 'user@example.com',
                cryptocurrency: 'ETH',
                threshold_price: 2500,
                threshold_percent: 3.0,
                condition: 'below',
                is_active: true,
                created_at: '2024-01-14T15:20:00Z'
            }
        ];
        
        alerts = mockAlerts;
        renderAlerts();
    } catch (error) {
        console.error('Ошибка загрузки алертов:', error);
        showNotification('Ошибка загрузки алертов', 'error');
    }
}

// Отображение алертов
function renderAlerts() {
    const container = document.getElementById('alertsList');
    const emptyState = document.getElementById('emptyState');
    const alertsSubtitle = document.getElementById('alertsSubtitle');
    const activeAlertsCount = document.getElementById('activeAlertsCount');
    
    const activeAlerts = alerts.filter(a => a.is_active);
    activeAlertsCount.textContent = activeAlerts.length;
    
    if (alerts.length === 0) {
        emptyState.style.display = 'block';
        alertsSubtitle.textContent = 'Все активные уведомления';
        return;
    }
    
    emptyState.style.display = 'none';
    alertsSubtitle.textContent = `${alerts.length} ${alerts.length === 1 ? 'алерт' : alerts.length < 5 ? 'алерта' : 'алертов'}`;
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item">
            <div class="alert-info">
                <div class="alert-crypto">${alert.cryptocurrency}</div>
                <div class="alert-details">
                    <div class="alert-detail-item">
                        <span style="color: var(--text-tertiary);">Email:</span>
                        <span>${alert.email}</span>
                    </div>
                    <div class="alert-detail-item">
                        <span style="color: var(--text-tertiary);">Порог:</span>
                        <span>$${formatPrice(alert.threshold_price)}</span>
                    </div>
                    <div class="alert-detail-item">
                        <span style="color: var(--text-tertiary);">Изменение:</span>
                        <span>${alert.threshold_percent}%</span>
                    </div>
                    <span class="badge ${alert.condition}">${alert.condition === 'above' ? 'Выше' : 'Ниже'}</span>
                    <span class="badge ${alert.is_active ? 'active' : 'inactive'}">
                        ${alert.is_active ? 'Активен' : 'Неактивен'}
                    </span>
                </div>
            </div>
            <div class="alert-actions">
                <button class="btn btn-danger btn-sm" onclick="openDeleteModal('${alert.id}')">
                    Удалить
                </button>
            </div>
        </div>
    `).join('');
}

// Создание алерта
async function handleCreateAlert(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const alertData = {
        email: formData.get('email'),
        cryptocurrency: formData.get('cryptocurrency'),
        threshold_percent: parseFloat(formData.get('thresholdPercent')),
        threshold_price: parseFloat(formData.get('thresholdPrice')),
        condition: formData.get('condition')
    };
    
    // Валидация
    if (!alertData.email || !alertData.cryptocurrency || !alertData.threshold_percent || !alertData.threshold_price) {
        showNotification('Заполните все поля', 'error');
        return;
    }
    
    try {
        // TODO: Заменить на реальный API вызов
        // const response = await fetch(`${API_BASE_URL}/alerts`, {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify(alertData)
        // });
        
        // if (!response.ok) {
        //     throw new Error('Ошибка создания алерта');
        // }
        
        // const newAlert = await response.json();
        
        // Мок ответ для демонстрации
        const newAlert = {
            id: Date.now().toString(),
            ...alertData,
            is_active: true,
            created_at: new Date().toISOString()
        };
        
        alerts.push(newAlert);
        renderAlerts();
        
        // Очистка формы
        e.target.reset();
        
        showNotification('Алерт успешно создан!', 'success');
    } catch (error) {
        console.error('Ошибка создания алерта:', error);
        showNotification('Ошибка создания алерта', 'error');
    }
}

// Удаление алерта
let alertToDelete = null;

function openDeleteModal(alertId) {
    alertToDelete = alertId;
    document.getElementById('deleteModal').classList.add('active');
}

function closeDeleteModal() {
    alertToDelete = null;
    document.getElementById('deleteModal').classList.remove('active');
}

async function handleDeleteAlert() {
    if (!alertToDelete) return;
    
    try {
        // TODO: Заменить на реальный API вызов
        // const response = await fetch(`${API_BASE_URL}/alerts/${alertToDelete}`, {
        //     method: 'DELETE'
        // });
        
        // if (!response.ok) {
        //     throw new Error('Ошибка удаления алерта');
        // }
        
        // Удаляем из массива
        alerts = alerts.filter(alert => alert.id !== alertToDelete);
        renderAlerts();
        
        closeDeleteModal();
        showNotification('Алерт успешно удален', 'success');
    } catch (error) {
        console.error('Ошибка удаления алерта:', error);
        showNotification('Ошибка удаления алерта', 'error');
    }
}

// Показ уведомлений
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Закрытие модального окна при клике вне его
document.getElementById('deleteModal').addEventListener('click', (e) => {
    if (e.target.id === 'deleteModal') {
        closeDeleteModal();
    }
});
