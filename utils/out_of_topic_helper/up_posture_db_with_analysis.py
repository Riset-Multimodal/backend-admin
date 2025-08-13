import os
import glob
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Posture
from supabase import create_client, Client
from concurrent.futures import ProcessPoolExecutor, as_completed

# -----------------------
# KONFIGURASI
# -----------------------
DB_URL = "postgresql://postgres:123@proxy.bccdev.id:11015/riset_db"
BASE_POSTURE_FOLDER = r"D:\Riset\python-scripts\uploads\posture"

SUPABASE_URL = "https://cnqvveimdkpztkjndvyp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNucXZ2ZWltZGtwenRram5kdnlwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDM2MTI5NSwiZXhwIjoyMDY5OTM3Mjk1fQ.ehY5xA0JSN6OYfayi7Gfw9OBKCsWj6RuTJOTBvJNRQw"
SUPABASE_BUCKET = "posture"

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_to_supabase(file_path, remote_name):
    with open(file_path, "rb") as f:
        file_data = f.read()

    supabase.storage.from_(SUPABASE_BUCKET).upload(
        remote_name,
        file_data,
        {"upsert": "true"}
    )

    url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(remote_name)
    return url


def process_single_capture(user_folder, capture_id, imgs, analysis_results):
    session = Session()
    try:
        print(f"📦 Simpan data posture: {user_folder}, capture_id={capture_id}")

        # Upload ke Supabase
        front_link = upload_to_supabase(imgs["front_image"], f"{user_folder}/{os.path.basename(imgs['front_image'])}")
        side_link = upload_to_supabase(imgs["side_image"], f"{user_folder}/{os.path.basename(imgs['side_image'])}")
        overhead_link = upload_to_supabase(imgs["overhead_image"], f"{user_folder}/{os.path.basename(imgs['overhead_image'])}")

        # Simpan ke DB
        posture_entry = Posture(
            user_email=user_folder.replace("_posture", ""),
            front_image_link=front_link,
            side_image_link=side_link,
            overhead_image_link=overhead_link,
            **analysis_results
        )

        session.add(posture_entry)
        session.commit()
        print(f"✅ Data posture {capture_id} tersimpan di DB.")
        return True

    except Exception as e:
        print(f"❌ Error {capture_id}: {e}")
        return False

    finally:
        session.close()


def process_posture_images():
    tasks = []
    with ProcessPoolExecutor(max_workers=10) as executor:
        for user_folder in os.listdir(BASE_POSTURE_FOLDER):
            folder_path = os.path.join(BASE_POSTURE_FOLDER, user_folder)
            if not os.path.isdir(folder_path):
                continue

            analysis_path = os.path.join(folder_path, "analysis_history.json")
            if not os.path.exists(analysis_path):
                print(f"⏭️ Lewati {user_folder}, tidak ada analysis_history.json")
                continue

            with open(analysis_path, "r") as f:
                try:
                    analysis_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️ Gagal parsing JSON untuk {user_folder}")
                    continue

            images = glob.glob(os.path.join(folder_path, "*.jpg"))
            if not images:
                print(f"⏭️ Lewati {user_folder}, tidak ada gambar .jpg")
                continue

            # Group berdasarkan capture_id
            capture_map = {}
            for img_path in images:
                filename = os.path.basename(img_path)
                parts = filename.split("_")
                if len(parts) < 3:
                    continue
                capture_id = f"{parts[0]}_{parts[1]}"
                if capture_id not in capture_map:
                    capture_map[capture_id] = {}
                if "front" in filename:
                    capture_map[capture_id]["front_image"] = img_path
                elif "side" in filename:
                    capture_map[capture_id]["side_image"] = img_path
                elif "overhead" in filename:
                    capture_map[capture_id]["overhead_image"] = img_path

            for capture_id, imgs in capture_map.items():
                if capture_id in analysis_data and all(k in imgs for k in ["front_image", "side_image", "overhead_image"]):
                    analysis_results = analysis_data[capture_id]["analysis_results"]
                    tasks.append(executor.submit(process_single_capture, user_folder, capture_id, imgs, analysis_results))
                else:
                    print(f"⚠️ Data tidak lengkap atau tidak ada analisis untuk {user_folder} - {capture_id}")

        # Tunggu semua selesai
        for future in as_completed(tasks):
            future.result()


if __name__ == "__main__":
    process_posture_images()
