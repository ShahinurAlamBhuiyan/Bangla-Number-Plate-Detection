# 🇧🇩 Bangladeshi License Plate Recognition (LPR)

A real-time Bangla license plate recognition system designed specifically for Bangladeshi vehicles.  
This project integrates YOLOv8 for vehicle and plate detection with EasyOCR for Bangla text recognition, creating a complete and efficient LPR pipeline.

---

## 🔗 Live Links

- 📓 **Colab Notebook:**  
  [Open in Google Colab](https://colab.research.google.com/drive/1lxFU_8wu-Xn_QOuzCEDzK4DgbzUb4PSC#scrollTo=dK5DpY9D5iiu)

- 📊 **Presentation Slides:**  
  [View Slides on Google Drive](https://docs.google.com/presentation/d/1Y48jeE3XRyTmcDbzbHdLjHq6smW-7Uon7YAaxUMqh9w/edit?usp=sharing)

---

## 📌 Features

- 🚗 **YOLOv8 Vehicle & Plate Detection**
- 🔠 **Bangla OCR with EasyOCR**
- 🧠 **Custom location logic** to extract city names from plates
- 📈 **Real-time pipeline** from video frame to data storage
- 📦 **Structured JSON output** for easy integration

---

## 🧠 Problem Statement

Most existing license plate recognition systems are built for **Latin characters** and perform poorly on Bangla plates due to:
- 🔤 **Lack of Bangla OCR support**
- 📉 **Scarcity of Bangladeshi plate datasets**
- 🧩 **No complete pipeline** for detection + recognition

Our system addresses all these with a modular, script-friendly design tailored for Bangladesh.

---

## 🛠️ Tech Stack

| Component         | Tool/Model     |
|------------------|----------------|
| Vehicle Detection | YOLOv8 (COCO)  |
| Plate Detection   | YOLOv8 (Custom)|
| OCR Engine        | EasyOCR (Bangla)|
| Image Processing  | OpenCV         |
| Storage           | JSON           |
| Platform          | Python, Google Colab |
| Database          | Mongodb |

---

## 🚀 How to Run (Colab)

1. Click on the **Colab link** above.
2. Run each cell in order.
3. Upload your input image/video as prompted.
4. Output (recognized text, plate info, and coordinates) will be saved to a downloadable `data.json`.

---

## 📊 Evaluation Metrics

- 🎯 **Detection Accuracy** – Using IOU and visual bounding box check
- ⚡ **Speed** – Frames per second (FPS)
- ✔️ **OCR Accuracy** – Compared against real license text

---

## 📚 Related Work

- 📈 **YOLOv8** – Balanced accuracy & speed (78% from prior study)
- 📘 **YOLOv10 + Tesseract** – 97% OCR accuracy in custom setups
- 💡 We used insights from both studies but chose YOLOv8 + EasyOCR for Bangla compatibility

---

## 🔮 Future Work

- 🚦 Real-time traffic surveillance systems
- 🏙️ Smart city vehicle analytics
- 🚔 Law enforcement tools (e.g., vehicle blacklist, alerts)
- 📷 Dashcam integration for roadside monitoring

---

## 👥 Contributors

- Shahinur Alam Bhuiyan
- Shahriar Khan

---

## 📜 License

This project is intended for educational and research purposes only. Not for commercial use.

---

⭐ If you find this helpful, consider giving the repo a star!

