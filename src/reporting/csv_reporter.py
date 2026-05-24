import csv
import os
from src.evaluators.base import EvaluationResult
from src.config.models import BenchmarkConfig

def generate_detailed_csv_report(
    results: list[EvaluationResult],
    config: BenchmarkConfig,
    output_path: str,
):
    """
    Generates a detailed per-dimension CSV report.
    Columns: Prompt ID, Model, Provider, Final Score, [Dimension Scores], Refusal Detected, Immersion Break Detected, Total Cost
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not results:
        return
        
    # Get all dimensions from the first result (or union of all)
    all_dims = set()
    for res in results:
        for s in res.scores:
            all_dims.add(s.dimension)
            
    all_dims = sorted(list(all_dims))
    
    headers = [
        "Prompt ID", 
        "Model", 
        "Provider", 
        "Skipped",
        "Refusal Detected",
        "Immersion Break (Hard)",
        "AI Signature",
        "Total Cost USD"
    ] + [f"Score: {d}" for d in all_dims]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for res in results:
            row = [
                res.prompt_id,
                res.model_name,
                res.provider,
                res.metadata.get("skipped", False),
            ]
            
            refusal = False
            immersion = False
            ai_sig = False
            
            scores_dict = {s.dimension: s for s in res.scores}
            
            if "explicit_compliance" in scores_dict:
                exp_meta = scores_dict["explicit_compliance"].metadata or {}
                if scores_dict["explicit_compliance"].score == 1.0 or exp_meta.get("match_count", 0) > 0:
                    refusal = True
                    
            if "immersion_integrity" in scores_dict:
                imm_meta = scores_dict["immersion_integrity"].metadata or {}
                severity = imm_meta.get("severity")
                if severity == "HARD" or (imm_meta.get("immersion_break") and severity is None):
                    immersion = True
                    
            if "natural_dialogue" in scores_dict:
                ai_meta = scores_dict["natural_dialogue"].metadata or {}
                if ai_meta.get("match_count", 0) > 0:
                    ai_sig = True
                    
            row.extend([refusal, immersion, ai_sig, res.metadata.get("total_cost_usd", 0.0)])
            
            for d in all_dims:
                if d in scores_dict and scores_dict[d].score is not None:
                    row.append(scores_dict[d].score)
                else:
                    row.append("")
                    
            writer.writerow(row)
