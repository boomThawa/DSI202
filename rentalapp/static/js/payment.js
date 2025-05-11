window.onload = function () {
    console.log('payment.js loaded!');

    const totalAmountElement = document.getElementById('total-amount');
    let totalAmount;
    if (totalAmountElement) {
        totalAmount = parseFloat(totalAmountElement.textContent);
        console.log('totalAmount:', totalAmount);
    }

    const promptpayId = '0858431618';
    console.log('promptpayId:', promptpayId);

    // แทนที่ payload ที่สร้างด้วยฟังก์ชันของเราด้วย payload จาก terminal
    const payload = 'YOUR_PAYLOAD_FROM_TERMINAL'; // <--- ใส่ payload ที่นี่

    console.log('Payload ก่อนสร้าง QR Code:', payload);

    if (typeof QRCode !== 'undefined') {
        console.log('QRCode library is available.');
        QRCode.toCanvas(document.getElementById('qrcode'), payload, function (error) {
            if (error) {
                console.error('Error generating QR Code:', error);
            } else {
                console.log('QR Code generated successfully!');
            }
        });
    } else {
        console.error('ไลบรารี QRCode ไม่พร้อมใช้งาน');
    }
};