import streamlit as st
import pandas as pd
import io
import chardet  # 💡 1. chardetをインポート

# 🎉 タイトルを装飾
st.markdown("<h1 style='color:#4A90E2;'>📑 振込リスト自動作成ツール</h1>", unsafe_allow_html=True)
st.markdown("アップロードしたCSVから発注先ごとの合計金額を算出し、Excelにまとめます。")
st.markdown("---")

uploaded_file = st.file_uploader("📂 CSVファイルをアップロード", type="csv")

if uploaded_file is not None:
    try:
        # 1. アップロードされたファイルをメモリにバイナリとして読み込む (必須)
        data = uploaded_file.getvalue()
        
        # 💡 2. chardet で文字コードを自動検出する
        result = chardet.detect(data)
        detected_encoding = result['encoding']
        
        if detected_encoding is None:
             # 検出できなかった場合は、安全な UTF-8 をデフォルトにする
             detected_encoding = 'utf-8'

        st.info(f"検出されたエンコーディング: {detected_encoding.upper()} で読み込みを試行します。")

        # 3. 検出したエンコーディングを使って読み込みを試行
        try:
            # 検出したエンコーディングで TextIOWrapper を作成
            stringio = io.TextIOWrapper(io.BytesIO(data), encoding=detected_encoding)
            df = pd.read_csv(stringio)
        except Exception as e:
            # 検出が失敗していた場合に、念のため Shift-JIS と UTF-8 を再試行
            if detected_encoding.lower() != 'shift_jis':
                stringio = io.TextIOWrapper(io.BytesIO(data), encoding='shift_jis')
                df = pd.read_csv(stringio)
                st.info("エンコーディング: Shift-JIS で再読み込みしました。")
            elif detected_encoding.lower() != 'utf-8':
                stringio = io.TextIOWrapper(io.BytesIO(data), encoding='utf-8')
                df = pd.read_csv(stringio)
                st.info("エンコーディング: UTF-8 で再読み込みしました。")
            else:
                raise e # 最終的に読み込めなかったらエラーを再発生

        # 4. 列名のチェックと集計処理 (以下、変更なし)
        if '発注先名' in df.columns and '振込額' in df.columns:
            df_summary = (
                df[['発注先名', '振込額']]
                .groupby('発注先名', as_index=False)
                .sum()
            )
            df_summary['フリガナ'] = ""
            df_summary = df_summary[['発注先名', 'フリガナ', '振込額']]

            # Excel書き出しとダウンロード
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_summary.to_excel(writer, index=False, sheet_name='振込リスト')
            buffer.seek(0)

            st.success("✅ 振込リストを作成しました！以下からダウンロードできます。")
            st.download_button(
                label="⬇️ 振込リストをダウンロード",
                data=buffer,
                file_name="振込リスト.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Excel形式でダウンロードできます"
            )
        else:
            st.error("⚠️ 読み込みはできましたが、'発注先名' または '振込額' の列がCSVに含まれていません。")
            st.dataframe(df.head())
            
    except Exception as e:
        # 最終エラーハンドリング
        st.error(f"❌ 最終的なエラーが発生しました。アプリの処理を確認してください: {e}")




