import qrcode

qr = qrcode.QRCode(box_size=10, border=4)
qr.add_data("https://google.com")
qr.make(fit=True)

img = qr.make_image()
img.save("test.png")
print("✅ QR Code test berhasil!")