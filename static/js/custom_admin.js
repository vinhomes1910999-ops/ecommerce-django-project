// Ví dụ: tự động focus vào ô tìm kiếm khi vào trang changelist
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('#searchbar');
    if (searchInput) {
        searchInput.focus();
    }
});