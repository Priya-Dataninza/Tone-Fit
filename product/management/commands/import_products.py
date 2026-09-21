import os
import pandas as pd
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from product.models import Product


class Command(BaseCommand):
    help = "Import products from final_women_dataset.xlsx"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(
            settings.BASE_DIR,
            "data",
            "final_women_dataset.xlsx"
        )

        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f"❌ File not found: {file_path}")
            )
            return

        self.stdout.write(self.style.WARNING("📂 Reading Excel file..."))

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading file: {e}"))
            return

        df = df.fillna("")

        total_rows = len(df)
        self.stdout.write(self.style.SUCCESS(f"📊 Total rows found: {total_rows}"))

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for index, row in df.iterrows():
            try:
                # Ensure unique product_id
                product_id = str(row.get("p_id") or f"P{index}").strip()

                if not product_id:
                    skipped_count += 1
                    continue

                # Extract image URL
                image_url = str(row.get("img", "")).strip()
                image_file = None

                # Download image from URL
                if image_url.startswith("http"):
                    try:
                        response = requests.get(image_url, timeout=10)
                        if response.status_code == 200:
                            image_name = image_url.split("/")[-1].split("?")[0]
                            image_file = ContentFile(
                                response.content,
                                name=image_name
                            )
                    except Exception:
                        pass  # Skip image if download fails

                # Create or update product
                product, created = Product.objects.update_or_create(
                    product_id=product_id,
                    defaults={
                        "product_name": str(row.get("name", "")),
                        "sub_category": str(row.get("products", "")),
                        "max_retail_price": int(
                            float(row.get("price", 0) or 0)
                        ),
                        "colour": str(row.get("colour", "")),
                        "brand": str(row.get("brand", "")),
                        "product_description": str(
                            row.get("description", "")
                        ),
                        "rating_count": int(
                            float(row.get("ratingCount", 0) or 0)
                        ),
                        "average_rating": float(
                            row.get("avg_rating", 0) or 0
                        ),
                    },
                )

                # Save image if available
                if image_file:
                    product.product_image.save(
                        image_file.name,
                        image_file,
                        save=True
                    )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                # Display progress every 100 records
                if (index + 1) % 100 == 0:
                    self.stdout.write(f"Processed {index + 1}/{total_rows} records...")

            except Exception as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Skipped row {index + 1}: {e}")
                )

        # Final Summary
        self.stdout.write(self.style.SUCCESS("\n✅ Import Completed!"))
        self.stdout.write(self.style.SUCCESS(f"📦 Created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"🔄 Updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"⚠️ Skipped: {skipped_count}"))