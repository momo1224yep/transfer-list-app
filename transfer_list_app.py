import streamlit as st
import pandas as pd
import io

# Streamlit UI
st.markdown("<h1 style='color:#4A90E2;'>📑 振込リスト自動作成ツール</h1>", unsafe_allow_html=True)
st.markdown("アップロードしたCSVから発注先ごとの合計金額を算出し、Excelにまとめます。")
st.markdown("---")

uploaded_file = st.file_uploader("📂 CSVファイルをアップロード", type="csv")

if uploaded_file is not None:
    try:
        df = None
        
        # --- ファイル読み込みの改善 ---
        # 1. まず Shift-JIS (日本の一般的なCSV) とカンマ区切りで試行
        try:
            df = pd.read_csv(uploaded_file, encoding="shift_jis")
            st.info("ファイルは Shift-JIS (カンマ区切り) として読み込まれました。")
        except:
            # 2. 失敗した場合、UTF-8 (一般的なWeb標準) とカンマ区切りで試行
            try:
                uploaded_file.seek(0) # ファイルポインタを先頭に戻す
                df = pd.read_csv(uploaded_file, encoding="utf-8")
                st.info("ファイルは UTF-8 (カンマ区切り) として読み込まれました。")
            except:
                # 3. 再度ファイルポインタを先頭に戻し、今度はShift-JISとタブ区切りで試行
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="shift_jis", sep='\t')
                    st.info("ファイルは Shift-JIS (タブ区切り) として読み込まれました。")
                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="utf-8", sep='\t')
                    st.info("ファイルは UTF-8 (タブ区切り) として読み込まれました。")
        
        if df is None or df.empty:
             st.error("⚠️ CSVファイルからデータを読み込めませんでした。ファイルが空であるか、エンコーディング・区切り文字が特殊かもしれません。")
             # return を st.stop() に変更してエラーを回避
             st.stop()

        # 必須列のチェック
        required_cols = ['発注先名', '振込額']
        
        # 処理に必要な列がデータフレームに含まれているか確認
        missing_cols = [col for col in required_cols if col not in df.columns]

        if not missing_cols:
            # 必須列のみを選択し、発注先名でグループ化して振込額を合計
            df_summary = (
                df[required_cols]
                .groupby('発注先名', as_index=False)
                .sum()
            )
            
            # フリガナ列を空で追加し、列の順番を調整
            df_summary['フリガナ'] = ""
            df_summary = df_summary[['発注先名', 'フリガナ', '振込額']]

            # ダウンロード用のExcelファイルを作成
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
            
            # プレビュー表示
            st.markdown("---")
            st.subheader("📝 作成されたリストのプレビュー")
            st.dataframe(df_summary, use_container_width=True)
            
        else:
            # 必須列が不足している場合のエラーメッセージ
            st.error(f"⚠️ 必須列が不足しています。以下の列名を確認してください: {', '.join(missing_cols)}")
            st.markdown("---")
            st.subheader("CSVの列ヘッダー一覧")
            st.dataframe(pd.DataFrame({'列名': df.columns}), use_container_width=True)

    except Exception as e:
        # その他、予期せぬエラーの表示
        st.error("❌ ファイル処理中に予期せぬエラーが発生しました。")
        st.code(f"エラー詳細: {e}")
