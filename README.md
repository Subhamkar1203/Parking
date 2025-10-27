

###  Smart Parking Dashboard

A **Streamlit-powered Smart Parking Monitoring System** using **OpenCV** and **computer vision** to detect free and occupied parking spaces in real time — from either a demo video or a live IP/RTSP camera feed.

---

##  Features

*  **Live Feed Support** — Monitor parking spaces from an IP/RTSP camera or demo video
*  **Real-Time Detection** — Uses OpenCV image processing to classify each spot as *Free* or *Occupied*
*  **Dynamic Dashboard** — Streamlit UI with live metrics, badges, and clean dark theme
*  **Smart Notifications** — Get instant toast alerts when a monitored spot changes status
*  **Spot Customization** — Choose which parking spots to monitor
*  **Modern UI** — Gradient buttons, clean layout, and responsive dashboard

---





##  Tech Stack

* **Python 3.8+**
* **Streamlit**
* **OpenCV (cv2)**
* **cvzone**
* **NumPy**
* **Pickle**

---

## ⚙️ Installation

1️⃣ **Clone this repository**

```bash
git clone https://github.com/Subhamkar1203/Parking.git
cd Parking
```

2️⃣ **Create a virtual environment (recommended)**

```bash
python -m venv venv
venv\Scripts\activate    # on Windows
# or
source venv/bin/activate # on Mac/Linux
```

3️⃣ **Install dependencies**

```bash
pip install -r requirements.txt
```

---

##  How to Run

```bash
streamlit run app.py
```

>  Make sure you have your **carPark.mp4** demo video and **CarParkPos** pickle file in the same directory.

---

##  Usage

* Select your video source from the sidebar (demo or IP stream).
* Pick specific spots to monitor, or enable **Monitor All**.
* The dashboard updates in real time with free and occupied spots.
* Toast notifications appear when a spot changes status.

---

## 🗂️ Project Structure

```
Parking/
│
├── app.py                 # Main Streamlit application
├── CarParkPos             # Pickle file storing parking spot coordinates
├── carPark.mp4            # Demo video feed
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

##  How to Create `CarParkPos`

To define your parking spot coordinates:

1. Run your `ParkingPicker.py` script (or your coordinate picker utility).
2. Draw rectangles over each parking spot.
3. Save — it creates a file named `CarParkPos`.

---

##  Future Improvements

* Add automatic number-plate recognition (ANPR)
* Cloud dashboard with historical parking analytics
* Mobile app or notification integration
* Parking fee calculation module

---

## 👨‍💻 Author

**Subham Kar**
🔗 [GitHub Profile](https://github.com/Subhamkar1203)

---



Would you like me to include a `requirements.txt` snippet (so users can install dependencies easily)?
