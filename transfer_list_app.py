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
        # 1. アップロードされたファイルをメモリにバイナリとして読み込む
        data = uploaded_file.getvalue() 
        
        # 2. 文字コードの試行錯誤ロジック (UTF-8を先に、Shift-JISを次に試す)
        try:
            # UTF-8で読み込みを試行 (Mac/Web標準)
            stringio = io.TextIOWrapper(io.BytesIO(data), encoding='utf-8')
            df = pd.read_csv(stringio)
            st.info("エンコーディング: UTF-8 で読み込みました。")
        except UnicodeDecodeError:
            # UTF-8で失敗した場合、Shift-JISで読み込みを試行 (Windows標準)
            # 💡 修正済み: 'shift_jis' -> 'shift_jis'
            stringio = io.TextIOWrapper(io.BytesIO(data), encoding='shift_jis') 
            df = pd.read_csv(stringio)
            st.info("エンコーディング: Shift-JIS で読み込みました。")
        except Exception as e:
            # どちらでも読み込めなかった場合の最終エラー
            st.error(f"❌ ファイルの読み込みに失敗しました。文字コードを確認してください: {e}")
            return
            
        # 3. 列名のチェックと集計処理
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






