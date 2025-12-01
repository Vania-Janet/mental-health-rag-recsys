"""Genera `ansiedad.json` usando los top N ASINs de `anxiety_counts_by_asin.csv`.

Si no existe `anxiety_counts_by_asin.csv`, el script recalcula los conteos desde
`kindle_reviews.csv` buscando la raíz 'anxiet' en `reviewText`.

Pero el json final solo incluye los top N ASINs.
El resto de la información se llena de forma manual después.

Ejemplo:
  python create_ansiedad_top50.py --top 50 --out ansiedad.json
"""
import argparse
import json
import os
import sys
import re

try:
    import pandas as pd
except Exception:
    print("pandas no está instalado. Instálalo con: pip install pandas", file=sys.stderr)
    raise


def read_counts_or_recompute(counts_csv: str, reviews_csv: str, pattern: str):
    # Si existe counts_csv, leer asin directamente
    if counts_csv and os.path.exists(counts_csv):
        try:
            df = pd.read_csv(counts_csv, dtype=str)
        except Exception:
            df = pd.read_csv(counts_csv, encoding='utf-8', dtype=str)
        # Aceptar diferentes nombres de columna, buscar 'asin'
        if 'asin' not in df.columns:
            possible = [c for c in df.columns if 'asin' in c.lower()]
            if possible:
                df = df.rename(columns={possible[0]: 'asin'})
            else:
                raise KeyError("El archivo de conteos no contiene columna 'asin'.")

        return df[['asin']]

    # Si no existe counts_csv, recalcular desde reviews_csv
    if not os.path.exists(reviews_csv):
        raise FileNotFoundError(f"No se encontró ni '{counts_csv}' ni '{reviews_csv}'.")

    try:
        df = pd.read_csv(reviews_csv, usecols=['asin', 'reviewText'], dtype=str)
    except Exception:
        df = pd.read_csv(reviews_csv, dtype=str)
        if 'asin' not in df.columns or 'reviewText' not in df.columns:
            raise KeyError("El CSV debe contener las columnas 'asin' y 'reviewText'.")
        df = df[['asin', 'reviewText']]

    df['reviewText'] = df['reviewText'].fillna('').astype(str)
    regex = re.compile(pattern, flags=re.IGNORECASE)
    mask = df['reviewText'].str.contains(regex)

    counts = df.loc[mask].groupby('asin').size().reset_index(name='count').sort_values('count', ascending=False)
    return counts[['asin']]


def build_json(asins, out_path: str):
    libros = []
    for a in asins:
        libros.append({
            "id": a,
            "titulo": "",
            "autor": "",
            "rating_amazon": "",
            "review_count": "",
            "cover_url": "",
            "por_que_leerlo": "",
        })

    out = {
        "ansiedad": {
            "titulo_seccion": "",
            "insight_big_data": "",
            "libros": libros,
        }
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Crear ansiedad.json con top N ASINs')
    parser.add_argument('--counts', '-c', default='anxiety_counts_by_asin.csv', help='CSV de conteos (generado previamente). Si no existe, se recalculará desde --reviews')
    parser.add_argument('--reviews', '-r', default='kindle_reviews.csv', help='CSV de reseñas para recalcular si hace falta')
    parser.add_argument('--out', '-o', default='ansiedad.json', help='Ruta de salida JSON')
    parser.add_argument('--top', '-t', default=50, type=int, help='Número de ASINs a incluir (por defecto 50)')
    parser.add_argument('--pattern', '-p', default=r'anxiet', help="Patrón regex para detectar menciones (por defecto 'anxiet')")

    args = parser.parse_args()

    try:
        df_asins = read_counts_or_recompute(args.counts, args.reviews, args.pattern)
    except Exception as e:
        print(f"Error al obtener ASINs: {e}", file=sys.stderr)
        sys.exit(1)

    top_asins = df_asins.head(args.top)['asin'].dropna().astype(str).tolist()

    build_json(top_asins, args.out)
    print(f"Escrito '{args.out}' con {len(top_asins)} entradas (top {len(top_asins)} ASINs).")


if __name__ == '__main__':
    main()
