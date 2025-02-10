# nuke_importer/utils/frame_utils.py
import re
import os


class FramePattern:
    def __init__(self):
        # Frame pattern tipleri
        self.patterns = [
            r'.*?[._](\d{6})\.[^.]+$',  # 6 haneli: 000001
            r'.*?[._](\d{5})\.[^.]+$',  # 5 haneli: 00001
            r'.*?[._](\d{4})\.[^.]+$',  # 4 haneli: 0001
            r'.*?[._](\d{3})\.[^.]+$',  # 3 haneli: 001
            r'.*?[._](\d{1,2})\.[^.]+$'  # 1-2 haneli: 1 veya 01
        ]

    def analyze_sequence(self, dirname, basename):
        """Dizindeki sequence dosyalarını analiz et"""
        try:
            # Dizindeki tüm dosyaları al
            files = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]

            # Base name'e uyan dosyaları filtrele
            base_pattern = re.escape(re.sub(r'\d+\.[^.]+$', '', basename))
            matching_files = [f for f in files if re.match(f"{base_pattern}\d+\.[^.]+$", f)]

            if not matching_files:
                return None

            # Frame numaralarını topla
            frames = []
            padding = None
            ext = None

            for f in matching_files:
                for pattern in self.patterns:
                    match = re.match(pattern, f)
                    if match:
                        frame_num = int(match.group(1))
                        padding = len(match.group(1))
                        ext = os.path.splitext(f)[1]
                        frames.append(frame_num)
                        break

            if frames:
                return {
                    'min_frame': min(frames),
                    'max_frame': max(frames),
                    'padding': padding,
                    'extension': ext,
                    'frame_count': len(frames),
                    'frames': sorted(frames)
                }

        except Exception as e:
            print(f"Error analyzing sequence: {str(e)}")
            return None

    def get_frame_path(self, sequence_dir, basename, frame_number, padding):
        """Belirli bir frame için dosya yolunu oluştur"""
        try:
            # Base pattern'i bul
            base = re.sub(r'\d+\.[^.]+$', '', basename)
            ext = os.path.splitext(basename)[1]

            # Frame numarasını formatla
            padded_num = str(frame_number).zfill(padding)

            # Dosya adını oluştur
            frame_name = f"{base}{padded_num}{ext}"

            # Tam yolu döndür
            return os.path.join(sequence_dir, frame_name)

        except Exception as e:
            print(f"Error getting frame path: {str(e)}")
            return None

    def get_first_frame_path(self, sequence_path):
        """Sequence path'inden ilk frame'in yolunu bul"""
        try:
            dirname = os.path.dirname(sequence_path)
            basename = os.path.basename(sequence_path)

            # Sequence analizi yap
            sequence_info = self.analyze_sequence(dirname, basename)

            if sequence_info:
                # İlk frame'in yolunu oluştur
                return self.get_frame_path(
                    dirname,
                    basename,
                    sequence_info['min_frame'],
                    sequence_info['padding']
                )

        except Exception as e:
            print(f"Error getting first frame path: {str(e)}")
            return None

    def get_frame_range_display(self, sequence_info):
        """Frame range bilgisini formatla"""
        if sequence_info:
            return f"{sequence_info['min_frame']}-{sequence_info['max_frame']}"
        return "Single Frame"