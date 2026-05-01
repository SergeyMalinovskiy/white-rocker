from stegosphere import image, binary_to_data, data_to_binary
from stegosphere.embeddings import LSB

# 1. Загружаем изображение
img = image.ImageContainer("maycat.png")
pixels = img.read()

# 2. Исходное сообщение (русские буквы, эмодзи — любые)
secret_msg = "Hello"

# 3. Преобразуем строку в бинарный вид (так stegosphere понимает любые символы)
binary_msg = data_to_binary(secret_msg)

# 4. Встраиваем сообщение в изображение
stego_pixels = LSB.embed(pixels, binary_msg)

# 5. Сохраняем результат
img.save("stego_image.png", stego_pixels)

# ---------- ИЗВЛЕКАЕМ ----------
# 6. Загружаем stego-изображение
stego_img = image.ImageContainer("stego_image.png")
stego_pixels = stego_img.read()

# 7. Извлекаем бинарные данные
extracted_binary = LSB.extract(stego_pixels)

# 8. Превращаем бинарные данные обратно в строку
decoded_msg = binary_to_data(extracted_binary).decode('utf-8')

print(decoded_msg)