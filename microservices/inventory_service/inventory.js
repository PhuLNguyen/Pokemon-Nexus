document.getElementById('loadInventory').addEventListener('click', async function() {
    const response = await fetch('/inventory/list');
    const result = await response.json();
    const list = document.getElementById('inventoryList');
    list.innerHTML = '';
    if (Array.isArray(result.items)) {
        result.items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            list.appendChild(li);
        });
    } else {
        list.innerHTML = '<li>No items found.</li>';
    }
});
