import streamlit as st
import pandas as pd
import io

# 🎉 タイトルを装飾
st.markdown("<h1 style='color:#4A90E2;'>📑 振込リスト自動作成ツール</h1>", unsafe_allow_html=True)
st.markdown("アップロードしたCSVから発注先ごとの合計金額を算出し、Excelにまとめます。")
st.markdown("---")

uploaded_file = st.file_uploader("📂 CSVファイルをアップロード", type="csv")

if uploaded_file is not None:
    try:
        try:
            df = pd.read_csv(uploaded_file, encoding="shift_jis")
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding="utf-8")

        if '発注先名' in df.columns and '振込額' in df.columns:
            df_summary = (
                df[['発注先名', '振込額']]
                .groupby('発注先名', as_index=False)
                .sum()
            )
            df_summary['フリガナ'] = ""
            df_summary = df_summary[['発注先名', 'フリガナ', '振込額']]

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
            st.error("⚠️ '発注先名' または '振込額' の列がCSVに含まれていません。")
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")



