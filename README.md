# Smart Fare – Dynamic Pricing Engine

A Django-based configurable pricing engine (like Uber/Ola) with a smart admin panel, dynamic pricing API, and comprehensive change logs.

---

## 🚀 Features

- **Admin-controlled Pricing Configs:**
  - Multiple pricing configs (only one active at a time)
  - Distance Base Price (DBP) by weekday
  - Distance Additional Price (DAP) per km after DBP
  - Time Multiplier Factor (TMF) based on ride duration slabs
  - Waiting Charges (WC) per X minutes after free wait time
  - Full change log for all config updates
- **Admin Interface:**
  - Powered by Django Admin with custom forms & validation
  - Inline editing for slabs and charges
  - Change log table for audit
- **Public Pricing API:**
  - `/api/calculate-price/` (POST)
  - Input: ride date, total distance, ride time, waiting time
  - Output: detailed pricing breakdown and final price
  - Returns errors for invalid/edge cases
- **Swagger & Redoc API Docs:**
  - `/swagger/` and `/redoc/` for interactive API docs
- **Unit-testable service logic**

---

## 🏗️ Project Structure

```
smart-fare/
├── config/           # Django project settings & URLs
├── engine/           # Core app: models, admin, API, services
├── venv/             # Virtual environment (ignored)
├── db.sqlite3        # Local DB (ignored by git)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## ⚙️ Setup & Installation

1. **Clone the repo:**
   ```sh
   git clone <your-repo-url>
   cd smart-fare
   ```
2. **Create & activate virtualenv:**
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
5. **Create superuser:**
   ```sh
   python manage.py createsuperuser
   ```
6. **Run the server:**
   ```sh
   python manage.py runserver
   ```

---

## 🛠️ Usage

- **Admin Panel:** `/admin/`
  - Create/edit pricing configs and slabs
  - Only one config can be active at a time
  - All changes are logged
- **API:** `/api/calculate-price/` (POST)
  - Example input:
    ```json
    {
      "ride_date": "2025-06-10",
      "total_distance_km": 7.5,
      "total_ride_time_min": 75,
      "waiting_time_min": 6
    }
    ```
  - Example output:
    ```json
    {
      "base_price": 90,
      "additional_distance_charge": 120,
      "time_multiplier_charge": 150,
      "waiting_charge": 10,
      "final_price": 370
    }
    ```
- **API Docs:**
  - Swagger: `/swagger/`
  - Redoc: `/redoc/`

---

## 🧪 Testing

- To run tests:
  ```sh
  python manage.py test engine
  ```

---

## 📝 Notes

- All pricing config changes are logged in `ConfigChangeLog` (see Admin).
- Only one config can be active at a time—this is enforced in admin.
- Edge cases (e.g., no active config, 0 distance/time) are handled gracefully by the API.

---

## 📧 Contact

For questions or issues, contact: [vinitchokshi1809@gmail.com](mailto:vinitchokshi1809@gmail.com)

---

Enjoy building with Smart Fare! 🚕
