document.addEventListener('DOMContentLoaded', function() {
    // Chỉ kích hoạt nếu đang ở trang Đăng nhập của Admin
    if (!document.querySelector('.login-box')) return;

    const inputs = document.querySelectorAll('.login-box .form-control');
    
    inputs.forEach(input => {
        const group = input.closest('.input-group');
        if (!group) return;

        // 1. Lấy chữ từ placeholder (VD: "Username", "Password") và giấu nó đi
        const labelText = input.getAttribute('placeholder') || 'Nhập thông tin';
        input.removeAttribute('placeholder');

        // 2. Tạo một cái nhãn (label) mới toanh và nhét vào giao diện
        const label = document.createElement('label');
        label.className = 'custom-float-label';
        label.innerText = labelText;
        group.appendChild(label);

        // 3. Hàm kiểm tra: Có chữ thì nổi lên, trống thì hạ xuống
        const checkValue = () => {
            if (input.value.trim() !== '') {
                group.classList.add('float-active');
            } else {
                if (document.activeElement !== input) {
                    group.classList.remove('float-active');
                }
            }
        };

        // Chạy kiểm tra ngay lần đầu lỡ trình duyệt tự điền sẵn mật khẩu
        setTimeout(checkValue, 100);

        // 4. Lắng nghe các thao tác của người dùng
        input.addEventListener('focus', () => group.classList.add('float-active'));
        input.addEventListener('blur', checkValue);
        input.addEventListener('input', checkValue);
    });
});