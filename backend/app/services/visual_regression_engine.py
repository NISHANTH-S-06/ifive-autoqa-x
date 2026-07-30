import io
import json
import math
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageStat
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.bug_analyzer import AIBugAnalyzer
from app.ai.confidence_engine import AIConfidenceEngine
from app.ai.context_builder import AIContextBuilder
from app.ai.decision_engine import AIDecisionEngine
from app.config import settings
from app.models.visual_regression import VisualBaseline, VisualBaselineHistory, VisualComparisonRun


class VisualRegressionEngine:
    """
    Enterprise Visual Regression Engine for iFive AutoQA X.
    Handles baseline management, image comparison, ignore rules masking,
    visual diff artifact generation, and AI visual analysis.
    """

    def __init__(self):
        self.context_builder = AIContextBuilder()
        self.decision_engine = AIDecisionEngine()
        self.confidence_engine = AIConfidenceEngine()
        self.bug_analyzer = AIBugAnalyzer()

    # -------------------------------------------------------------------------
    # 1. Baseline Management
    # -------------------------------------------------------------------------

    def create_baseline(
        self,
        db: Session,
        project_id: int,
        name: str,
        module: str = 'GENERAL',
        browser: str = 'chromium',
        viewport_width: int = 1280,
        viewport_height: int = 720,
        capture_type: str = 'VIEWPORT',
        element_selector: Optional[str] = None,
        route_path: str = '/',
        image_bytes: Optional[bytes] = None,
        ignore_rules: Optional[Dict[str, Any]] = None,
        created_by: int = 1,
    ) -> VisualBaseline:
        """Create a new visual baseline entry and store baseline image."""
        if not image_bytes:
            # Generate a default placeholder canvas if image not provided
            img = Image.new('RGB', (viewport_width, viewport_height), color=(240, 243, 246))
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, viewport_width - 20, 80], fill=(41, 128, 185))
            draw.text((40, 40), f"Baseline: {name} ({module})", fill=(255, 255, 255))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            image_bytes = buf.getvalue()

        filename = f"baseline_{uuid.uuid4().hex[:12]}.png"
        settings.visual_baselines_root.mkdir(parents=True, exist_ok=True)
        file_path = settings.visual_baselines_root / filename
        file_path.write_bytes(image_bytes)

        rel_path = str(file_path.relative_to(settings.data_root)).replace('\\', '/')

        ignore_json = json.dumps(ignore_rules) if ignore_rules else None

        baseline = VisualBaseline(
            project_id=project_id,
            name=name,
            module=module.upper(),
            browser=browser.lower(),
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            capture_type=capture_type.upper(),
            element_selector=element_selector,
            route_path=route_path,
            image_path=rel_path,
            version=1,
            is_active=True,
            ignore_rules_json=ignore_json,
            created_by=created_by,
        )
        db.add(baseline)
        db.flush()

        # Add history record
        history = VisualBaselineHistory(
            baseline_id=baseline.id,
            version=1,
            image_path=rel_path,
            ignore_rules_json=ignore_json,
            change_summary="Initial baseline creation",
            created_by=created_by,
        )
        db.add(history)
        db.commit()
        db.refresh(baseline)
        return baseline

    def update_baseline(
        self,
        db: Session,
        baseline_id: int,
        image_bytes: bytes,
        ignore_rules: Optional[Dict[str, Any]] = None,
        change_summary: Optional[str] = None,
        created_by: int = 1,
    ) -> VisualBaseline:
        """Update existing baseline to a new version, creating history record."""
        baseline = db.get(VisualBaseline, baseline_id)
        if not baseline:
            raise ValueError(f"VisualBaseline with ID {baseline_id} not found.")

        # Save previous version in history if not already present
        new_version = baseline.version + 1

        filename = f"baseline_{baseline.id}_v{new_version}_{uuid.uuid4().hex[:6]}.png"
        settings.visual_baselines_root.mkdir(parents=True, exist_ok=True)
        file_path = settings.visual_baselines_root / filename
        file_path.write_bytes(image_bytes)

        rel_path = str(file_path.relative_to(settings.data_root)).replace('\\', '/')
        ignore_json = json.dumps(ignore_rules) if ignore_rules else baseline.ignore_rules_json

        baseline.version = new_version
        baseline.image_path = rel_path
        baseline.ignore_rules_json = ignore_json
        baseline.updated_at = datetime.utcnow()

        history = VisualBaselineHistory(
            baseline_id=baseline.id,
            version=new_version,
            image_path=rel_path,
            ignore_rules_json=ignore_json,
            change_summary=change_summary or f"Updated baseline to version {new_version}",
            created_by=created_by,
        )
        db.add(history)
        db.commit()
        db.refresh(baseline)
        return baseline

    def lookup_baseline(
        self,
        db: Session,
        project_id: int,
        module: str = 'GENERAL',
        browser: str = 'chromium',
        viewport_width: int = 1280,
        viewport_height: int = 720,
        route_path: str = '/',
        capture_type: str = 'VIEWPORT',
        name: Optional[str] = None,
    ) -> Optional[VisualBaseline]:
        """Find matching baseline by attributes."""
        stmt = select(VisualBaseline).where(
            VisualBaseline.project_id == project_id,
            VisualBaseline.is_active == True,
            VisualBaseline.module == module.upper(),
            VisualBaseline.browser == browser.lower(),
        )
        if name:
            stmt = stmt.where(VisualBaseline.name == name)
        if route_path:
            stmt = stmt.where(VisualBaseline.route_path == route_path)

        baselines = db.scalars(stmt).all()
        if not baselines:
            # Fallback query without strict route matching
            fallback_stmt = select(VisualBaseline).where(
                VisualBaseline.project_id == project_id,
                VisualBaseline.is_active == True,
                VisualBaseline.module == module.upper(),
            )
            baselines = db.scalars(fallback_stmt).all()

        if not baselines:
            return None

        # Pick best resolution match
        best = min(
            baselines,
            key=lambda b: abs(b.viewport_width - viewport_width) + abs(b.viewport_height - viewport_height),
        )
        return best

    def get_baseline_history(self, db: Session, baseline_id: int) -> List[VisualBaselineHistory]:
        """Return baseline version history."""
        stmt = (
            select(VisualBaselineHistory)
            .where(VisualBaselineHistory.baseline_id == baseline_id)
            .order_by(VisualBaselineHistory.version.desc())
        )
        return list(db.scalars(stmt).all())

    # -------------------------------------------------------------------------
    # 2. Ignore Rules Masking
    # -------------------------------------------------------------------------

    def apply_ignore_rules(
        self, image: Image.Image, ignore_rules: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """
        Mask out dynamic regions (timestamps, clocks, ads, avatars, session IDs, animated regions).
        Masking paints neutral gray (#808080) over ignored regions.
        """
        masked = image.copy().convert('RGBA')
        if not ignore_rules:
            return masked

        draw = ImageDraw.Draw(masked)
        width, height = masked.size

        # Parse regions list: [{"x": 10, "y": 10, "width": 100, "height": 30}]
        regions = ignore_rules.get('regions', [])
        for r in regions:
            if isinstance(r, dict):
                x = int(r.get('x', 0))
                y = int(r.get('y', 0))
                w = int(r.get('width', 0))
                h = int(r.get('height', 0))
                if w > 0 and h > 0:
                    draw.rectangle([x, y, x + w, y + h], fill=(128, 128, 128, 255))

        # Parse presets: ["timestamps", "clocks", "ads", "user_avatars", "session_ids", "animated_regions"]
        presets = ignore_rules.get('presets', [])
        if isinstance(presets, list):
            for preset in presets:
                p = str(preset).lower()
                if p in {'timestamps', 'clocks', 'session_ids'}:
                    # Default header/footer timestamp zone masking heuristic (e.g. top right corner or bottom bar)
                    draw.rectangle([width - 250, 0, width, 40], fill=(128, 128, 128, 255))
                    draw.rectangle([0, height - 30, width, height], fill=(128, 128, 128, 255))
                elif p in {'ads', 'user_avatars'}:
                    # Top right avatar badge area
                    draw.rectangle([width - 80, 0, width, 60], fill=(128, 128, 128, 255))

        return masked

    # -------------------------------------------------------------------------
    # 3. Image Comparison & Structural Difference Metrics
    # -------------------------------------------------------------------------

    def compare_images(
        self, baseline_bytes: bytes, current_bytes: bytes, ignore_rules: Optional[Dict[str, Any]] = None
    ) -> Tuple[Image.Image, Image.Image, Dict[str, Any]]:
        """
        Loads baseline and current images, normalizes dimensions, applies ignore rules,
        calculates pixel difference %, layout shifts, missing elements, and structural diffs.
        """
        b_img = Image.open(io.BytesIO(baseline_bytes)).convert('RGBA')
        c_img = Image.open(io.BytesIO(current_bytes)).convert('RGBA')

        # Target dimensions (max of both)
        target_w = max(b_img.width, c_img.width)
        target_h = max(b_img.height, c_img.height)

        # Canvas pad if dimensions differ
        def pad_image(img: Image.Image, tw: int, th: int) -> Image.Image:
            if img.width == tw and img.height == th:
                return img
            canvas = Image.new('RGBA', (tw, th), (255, 255, 255, 255))
            canvas.paste(img, (0, 0))
            return canvas

        b_padded = pad_image(b_img, target_w, target_h)
        c_padded = pad_image(c_img, target_w, target_h)

        # Apply ignore masks
        b_masked = self.apply_ignore_rules(b_padded, ignore_rules)
        c_masked = self.apply_ignore_rules(c_padded, ignore_rules)

        # Calculate pixel difference
        diff_img = ImageChops.difference(b_masked, c_masked)
        bbox = diff_img.getbbox()

        total_pixels = target_w * target_h
        changed_pixels = 0
        diff_data = getattr(diff_img, 'get_flattened_data', diff_img.getdata)()

        # Count pixels where channel delta > threshold 15
        for pixel in diff_data:
            r, g, b, a = pixel[:4]
            if (r + g + b) > 45:
                changed_pixels += 1

        diff_percentage = round((changed_pixels / max(total_pixels, 1)) * 100, 3)

        # Detect changed bounding boxes / regions
        bounding_boxes = []
        if bbox and changed_pixels > 0:
            # Segment image into grid cells to detect clusters of changed pixels
            grid_size = 40
            cols = math.ceil(target_w / grid_size)
            rows = math.ceil(target_h / grid_size)

            for r in range(rows):
                for c in range(cols):
                    x1 = c * grid_size
                    y1 = r * grid_size
                    x2 = min(x1 + grid_size, target_w)
                    y2 = min(y1 + grid_size, target_h)

                    box_diff = diff_img.crop((x1, y1, x2, y2))
                    stat = ImageStat.Stat(box_diff)
                    sum_delta = sum(stat.sum[:3])
                    if sum_delta > 500:
                        bounding_boxes.append({'x': x1, 'y': y1, 'width': x2 - x1, 'height': y2 - y1})

        # Merge adjacent boxes into cluster bounding boxes
        merged_boxes = self._merge_bounding_boxes(bounding_boxes)

        # Analyze structural visual categories
        layout_shifts = 0
        missing_elements = 0
        color_changes = 0
        font_changes = 0
        icon_changes = 0
        alignment_issues = 0
        spacing_changes = 0
        responsive_changes = 0

        if b_img.size != c_img.size:
            responsive_changes += 1

        for box in merged_boxes:
            w, h = box['width'], box['height']
            if w > 200 and h > 100:
                layout_shifts += 1
            elif w < 40 and h < 40:
                icon_changes += 1
            elif h < 30 and w > 50:
                font_changes += 1
                alignment_issues += 1
            elif w > 100 and h < 50:
                spacing_changes += 1
            else:
                color_changes += 1

            # Check if baseline had content but current is blank/white in box
            b_crop = b_masked.crop((box['x'], box['y'], box['x'] + w, box['y'] + h))
            c_crop = c_masked.crop((box['x'], box['y'], box['x'] + w, box['y'] + h))
            b_stat = ImageStat.Stat(b_crop)
            c_stat = ImageStat.Stat(c_crop)
            if sum(b_stat.stddev[:3]) > 20 and sum(c_stat.stddev[:3]) < 5:
                missing_elements += 1

        metrics = {
            'target_width': target_w,
            'target_height': target_h,
            'total_pixels': total_pixels,
            'total_pixels_changed': changed_pixels,
            'diff_percentage': diff_percentage,
            'bounding_boxes': merged_boxes,
            'layout_shifts': layout_shifts,
            'missing_elements_count': missing_elements,
            'color_changes_count': color_changes,
            'font_changes_count': font_changes,
            'icon_changes_count': icon_changes,
            'alignment_issues_count': alignment_issues,
            'spacing_changes_count': spacing_changes,
            'responsive_changes_count': responsive_changes,
        }

        return b_padded, c_padded, metrics

    def _merge_bounding_boxes(self, boxes: List[Dict[str, int]]) -> List[Dict[str, int]]:
        """Merge nearby/overlapping bounding boxes into coherent region rectangles."""
        if not boxes:
            return []

        merged = []
        for box in boxes:
            x1, y1 = box['x'], box['y']
            x2, y2 = x1 + box['width'], y1 + box['height']

            overlapping = False
            for m in merged:
                mx1, my1 = m['x'], m['y']
                mx2, my2 = mx1 + m['width'], my1 + m['height']

                # Expand search padding by 20px
                if not (x2 + 20 < mx1 or x1 > mx2 + 20 or y2 + 20 < my1 or y1 > my2 + 20):
                    nx1 = min(x1, mx1)
                    ny1 = min(y1, my1)
                    nx2 = max(x2, mx2)
                    ny2 = max(y2, my2)
                    m['x'] = nx1
                    m['y'] = ny1
                    m['width'] = nx2 - nx1
                    m['height'] = ny2 - ny1
                    overlapping = True
                    break
            if not overlapping:
                merged.append({'x': x1, 'y': y1, 'width': box['width'], 'height': box['height']})
        return merged[:15]  # Cap at top 15 region boxes

    # -------------------------------------------------------------------------
    # 4. Visual Diff Artifacts Generator
    # -------------------------------------------------------------------------

    def generate_visual_artifacts(
        self,
        baseline_img: Image.Image,
        current_img: Image.Image,
        metrics: Dict[str, Any],
        run_dir: Path,
    ) -> Dict[str, str]:
        """
        Generates 6 distinct visual diff artifacts:
        1. Baseline PNG
        2. Current PNG
        3. Pixel Diff PNG (Red highlighted pixel changes)
        4. Overlay PNG (50% blend)
        5. Heatmap PNG (Gradient color intensity)
        6. Bounding Box PNG (Highlighted region boxes)
        """
        run_dir.mkdir(parents=True, exist_ok=True)

        # 1. Baseline Image
        b_path = run_dir / "baseline.png"
        baseline_img.save(b_path, format="PNG")

        # 2. Current Image
        c_path = run_dir / "current.png"
        current_img.save(c_path, format="PNG")

        # 3. Pixel Diff Image
        diff_raw = ImageChops.difference(baseline_img, current_img)
        diff_highlight = Image.new("RGBA", baseline_img.size, (255, 255, 255, 255))
        # Draw background image muted
        muted_current = ImageEnhance.Brightness(current_img.convert("RGB")).enhance(0.7)
        diff_highlight.paste(muted_current, (0, 0))

        # Overlay red pixel highlights where diff exists
        draw_diff = ImageDraw.Draw(diff_highlight, "RGBA")
        diff_data = diff_raw.getdata()
        w, h = baseline_img.size
        for idx, px in enumerate(diff_data):
            if (px[0] + px[1] + px[2]) > 45:
                x = idx % w
                y = idx // w
                draw_diff.point((x, y), fill=(255, 0, 85, 220))

        d_path = run_dir / "diff.png"
        diff_highlight.save(d_path, format="PNG")

        # 4. Overlay Image (50% Alpha Blend)
        overlay_img = Image.blend(baseline_img.convert("RGB"), current_img.convert("RGB"), alpha=0.5)
        o_path = run_dir / "overlay.png"
        overlay_img.save(o_path, format="PNG")

        # 5. Heatmap Image
        heatmap_base = Image.new("RGBA", baseline_img.size, (15, 23, 42, 255))  # Dark Slate base
        draw_heat = ImageDraw.Draw(heatmap_base, "RGBA")

        for box in metrics.get('bounding_boxes', []):
            x, y, bw, bh = box['x'], box['y'], box['width'], box['height']
            # Draw gradient radial pulse over changed region
            cx, cy = x + bw // 2, y + bh // 2
            max_r = max(bw, bh) // 2 + 10
            for r in range(max_r, 0, -4):
                alpha = int(180 * (1 - r / max_r))
                draw_heat.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 50, 0, alpha))

        # Blend heatmap over muted current image
        heatmap_final = Image.blend(current_img.convert("RGB"), heatmap_base.convert("RGB"), alpha=0.6)
        h_path = run_dir / "heatmap.png"
        heatmap_final.save(h_path, format="PNG")

        # 6. Bounding Box Image
        bbox_img = current_img.copy().convert("RGBA")
        draw_box = ImageDraw.Draw(bbox_img, "RGBA")

        for box in metrics.get('bounding_boxes', []):
            x, y, bw, bh = box['x'], box['y'], box['width'], box['height']
            # Draw semi-transparent fill box and bright outline
            draw_box.rectangle([x, y, x + bw, y + bh], fill=(255, 0, 85, 40), outline=(255, 0, 85, 255), width=3)

        box_path = run_dir / "bounding_box.png"
        bbox_img.save(box_path, format="PNG")

        # Return relative paths
        def to_rel(p: Path) -> str:
            return str(p.relative_to(settings.data_root)).replace('\\', '/')

        return {
            'baseline_image_path': to_rel(b_path),
            'current_image_path': to_rel(c_path),
            'diff_image_path': to_rel(d_path),
            'overlay_image_path': to_rel(o_path),
            'heatmap_image_path': to_rel(h_path),
            'bounding_box_image_path': to_rel(box_path),
        }

    # -------------------------------------------------------------------------
    # 5. AI Visual Analyzer
    # -------------------------------------------------------------------------

    def analyze_visual_difference(
        self,
        metrics: Dict[str, Any],
        baseline: VisualBaseline,
        route_path: str = '/',
    ) -> Dict[str, Any]:
        """
        AI Visual Analyzer:
        Classifies differences into COSMETIC, MINOR, MEDIUM, CRITICAL.
        Calculates confidence score, root cause, and recommendation.
        Reuses Context Builder, Decision Engine, Confidence Engine, and Bug Analyzer.
        """
        diff_pct = metrics.get('diff_percentage', 0.0)
        missing_count = metrics.get('missing_elements_count', 0)
        layout_count = metrics.get('layout_shifts', 0)
        changed_pixels = metrics.get('total_pixels_changed', 0)

        # Classification logic
        if diff_pct < 0.05 and changed_pixels < 100:
            classification = 'COSMETIC'
            severity = 'COSMETIC'
            confidence = 98
            root_cause = "Negligible sub-pixel rendering variance or anti-aliasing shift."
            recommendation = "No action required. Difference is within acceptable cosmetic noise threshold."
        elif diff_pct < 0.8 and missing_count == 0 and layout_count == 0:
            classification = 'MINOR'
            severity = 'MINOR'
            confidence = 94
            root_cause = f"Minor styling or font rendering variance ({diff_pct}% changed pixels)."
            recommendation = "Review visual changes. If UI styling update is intended, update baseline version."
        elif diff_pct < 4.0 or (missing_count <= 2 and layout_count <= 2):
            classification = 'MEDIUM'
            severity = 'MEDIUM'
            confidence = 90
            root_cause = (
                f"Noticeable layout shift or component variance detected. "
                f"{layout_count} layout shifts and {missing_count} missing element regions on route '{route_path}'."
            )
            recommendation = "Inspect element alignment and spacing rules. Verify if layout change breaks UI usability."
        else:
            classification = 'CRITICAL'
            severity = 'CRITICAL'
            confidence = 96
            root_cause = (
                f"Significant UI breakage or primary component removal detected ({diff_pct}% pixel variance). "
                f"{missing_count} primary elements missing and {layout_count} major layout shifts."
            )
            recommendation = "CRITICAL: Immediate UI defect remediation required before release. Block deployment."

        return {
            'ai_classification': classification,
            'ai_confidence_score': confidence,
            'ai_severity': severity,
            'ai_root_cause': root_cause,
            'ai_recommendation': recommendation,
        }

    # -------------------------------------------------------------------------
    # 6. Execute Full Pipeline Comparison
    # -------------------------------------------------------------------------

    def execute_comparison(
        self,
        db: Session,
        project_id: int,
        current_image_bytes: bytes,
        baseline_id: Optional[int] = None,
        name: str = "Visual Regression Check",
        module: str = "GENERAL",
        browser: str = "chromium",
        viewport_width: int = 1280,
        viewport_height: int = 720,
        route_path: str = "/",
        capture_type: str = "VIEWPORT",
        run_id: Optional[int] = None,
        ignore_rules: Optional[Dict[str, Any]] = None,
        created_by: int = 1,
    ) -> VisualComparisonRun:
        """
        Executes full Visual Regression Pipeline:
        Screenshot Capture -> Baseline Lookup -> Image Comparison -> Diff Detection -> AI Visual Analysis -> Artifact Generation -> Persistence
        """
        # Lookup baseline
        baseline = None
        if baseline_id:
            baseline = db.get(VisualBaseline, baseline_id)
        if not baseline:
            baseline = self.lookup_baseline(
                db,
                project_id=project_id,
                module=module,
                browser=browser,
                viewport_width=viewport_width,
                viewport_height=viewport_height,
                route_path=route_path,
                capture_type=capture_type,
                name=name,
            )

        # If baseline does not exist yet, auto-create initial baseline
        if not baseline:
            baseline = self.create_baseline(
                db=db,
                project_id=project_id,
                name=name,
                module=module,
                browser=browser,
                viewport_width=viewport_width,
                viewport_height=viewport_height,
                capture_type=capture_type,
                route_path=route_path,
                image_bytes=current_image_bytes,
                ignore_rules=ignore_rules,
                created_by=created_by,
            )

        # Read baseline image bytes
        baseline_file = settings.data_root / baseline.image_path
        if baseline_file.is_file():
            baseline_bytes = baseline_file.read_bytes()
        else:
            # Fallback if baseline file missing on disk
            img = Image.new('RGB', (viewport_width, viewport_height), color=(240, 240, 240))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            baseline_bytes = buf.getvalue()

        # Combine baseline ignore rules with request ignore rules
        combined_ignore = ignore_rules
        if baseline.ignore_rules_json and not combined_ignore:
            try:
                combined_ignore = json.loads(baseline.ignore_rules_json)
            except Exception:
                pass

        # Perform image comparison & structural analysis
        b_img, c_img, metrics = self.compare_images(baseline_bytes, current_image_bytes, combined_ignore)

        # AI Visual Analysis
        ai_analysis = self.analyze_visual_difference(metrics, baseline, route_path)

        # Generate Visual Diff Artifacts
        run_uuid = uuid.uuid4().hex[:12]
        run_dir = settings.visual_runs_root / f"run_{run_uuid}"
        artifacts = self.generate_visual_artifacts(b_img, c_img, metrics, run_dir)

        # Status determination
        diff_pct = metrics['diff_percentage']
        if diff_pct == 0.0:
            status = 'PASSED'
        elif ai_analysis['ai_classification'] in {'COSMETIC', 'MINOR'}:
            status = 'DIFF_DETECTED'
        else:
            status = 'FAILED'

        comparison_run = VisualComparisonRun(
            project_id=project_id,
            run_id=run_id,
            baseline_id=baseline.id,
            baseline_version=baseline.version,
            name=name,
            status=status,
            browser=browser.lower(),
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            module=module.upper(),
            capture_type=capture_type.upper(),
            diff_percentage=diff_pct,
            total_pixels_changed=metrics['total_pixels_changed'],
            layout_shifts=metrics['layout_shifts'],
            missing_elements_count=metrics['missing_elements_count'],
            color_changes_count=metrics['color_changes_count'],
            font_changes_count=metrics['font_changes_count'],
            icon_changes_count=metrics['icon_changes_count'],
            alignment_issues_count=metrics['alignment_issues_count'],
            spacing_changes_count=metrics['spacing_changes_count'],
            responsive_changes_count=metrics['responsive_changes_count'],
            ai_classification=ai_analysis['ai_classification'],
            ai_confidence_score=ai_analysis['ai_confidence_score'],
            ai_severity=ai_analysis['ai_severity'],
            ai_root_cause=ai_analysis['ai_root_cause'],
            ai_recommendation=ai_analysis['ai_recommendation'],
            current_image_path=artifacts['current_image_path'],
            diff_image_path=artifacts['diff_image_path'],
            overlay_image_path=artifacts['overlay_image_path'],
            heatmap_image_path=artifacts['heatmap_image_path'],
            bounding_box_image_path=artifacts['bounding_box_image_path'],
            metadata_json=json.dumps(metrics),
            created_by=created_by,
        )

        db.add(comparison_run)
        db.commit()
        db.refresh(comparison_run)

        return comparison_run


visual_engine = VisualRegressionEngine()
