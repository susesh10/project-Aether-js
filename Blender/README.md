# Akari 3D Model – Blender Workspace

This folder contains all 3D modelling assets for **Akari**, the AI companion of Project Aether.

---

## 🎯 Character Overview

- **Name**: Akari (灯)
- **Style**: Balanced (Realistic body proportions + Stylized anime face)
- **Inspiration**: Marin Kitagawa + elegant Shizuku Kuroe influence
- **Purpose**: High-quality 3D model for the AI companion interface (later usable in React / Three.js)

---

## 📏 Finalized Measurements

| Measurement              | Value     | Notes |
|--------------------------|-----------|-------|
| Total Height             | 164 cm    | Official Marin height |
| Head Height              | 22 cm     | ≈ 7.5 heads tall (balanced) |
| Shoulder Width           | 35 cm     | Official data |
| Bust                     | 86.8 cm   | Official |
| Underbust                | 68.2 cm   | Official |
| Waist                    | 58.7 cm   | Official |
| Hips                     | 84.8 cm   | Official |
| Inseam                   | 79.2 cm   | Official |
| Arm Length (shoulder→wrist) | ≈ 52 cm | Approximate |

---

## 📁 Folder Structure

project-aether-js/
├── backend/
├── frontend/
├── blender/                          ← Main Blender folder
│   ├── references/                   ← All reference images
│   │   ├── front_view.png
│   │   ├── side_view.png
│   │   ├── three_quarter_view.png
│   │   ├── expressions.png
│   │   └── hair_options.png
│   │
│   ├── akari_model/                  ← Your actual Blender files
│   │   ├── akari_head.blend          ← Main working file
│   │   ├── akari_head_v1.blend       ← Versions (optional)
│   │   └── exports/                  ← Exported models later
│   │
│   └── textures/                     ← Textures (if any)
│       └── ...
│
├── README.md
└── ...

---

## 🖼️ Current Reference Images

- Full body multi-view sheet (with measurements)
- Front View (with facial guidelines)
- Left Side View
- Right Side View
- Back View
- Expression Sheet
- Hair Reference (Marin blonde + Shizuku dark styles)

---

## 🛠️ Modelling Plan

1. **Head Blockout** (Box modelling + Mirror + Subdivision)
2. Face sculpting (anime stylized)
3. Basic hair
4. Materials & basic lighting
5. Bust / Upper body
6. Full body (using official measurements)
7. Clothing
8. Final detailing + export

---

## 📌 Notes

- Always keep the **Head Height = 22 cm** consistent when scaling.
- Use Front + Side views together for accurate proportions.
- Prefer clean topology for future animation / expressions.
- Save versions regularly (`akari_head_v1.blend`, `v2`, etc.).

---

**Last Updated**: July 2026
