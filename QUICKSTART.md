# 🚀 **QUICK START GUIDE**

Get Sentinel-Net running locally in **5 minutes**.

---

## ✅ **Prerequisites**

- ✅ Python 3.12 installed globally (you're installing now)
- ✅ Git installed
- ✅ This repository cloned

---

## 📋 **Setup Steps**

### Step 1: Create Virtual Environment

```bash
cd c:\Sami\Sentinal-net

python -m venv venv

venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Wait ~2-3 minutes. You'll see lots of installation messages.

### Step 3: Setup Environment Config

```bash
cp .env.example .env
```

(Edit `.env` if needed - defaults work for local development)

### Step 4: Verify Installation

```bash
python -c "import fastapi; import sklearn; import pandas; print('✓ All dependencies installed successfully!')"
```

You should see: `✓ All dependencies installed successfully!`

---

## 🎯 **Phase 2: Ready to Begin**

Once Python is installed and dependencies are set up:

**Next:** Phase 2 - Data Pipeline
- Download SMS dataset
- Build preprocessor
- Test data loading

**Command to start Phase 2:**
```bash
python backend/data/loader.py
```

---

## 🔧 **Common Issues**

### Issue: `python: command not found`

**Solution:**
```bash
# Check if Python is in PATH
where python

# If not found, add to PATH:
# Windows Settings → Environment Variables → PATH
# Add: C:\Users\YourUsername\AppData\Local\Programs\Python\Python312
```

### Issue: `pip: command not found`

**Solution:**
```bash
python -m pip install --upgrade pip
```

### Issue: Virtual environment won't activate

**Solution:**
```bash
# Delete and recreate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
```

---

## 📚 **Full Documentation**

- 📖 [Main README](README.md)
- 👨‍💻 [Developer Setup](docs/developer/README.md)
- 📊 [Metrics Guide](docs/metrics/README.md)
- 💼 [Stakeholder Brief](docs/stakeholder/README.md)

---

**✨ You're ready to start Phase 2 once Python is installed!**
