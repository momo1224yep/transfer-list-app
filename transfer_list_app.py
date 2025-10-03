import streamlit as st
import pandas as pd
import io

# Streamlit UI
st.markdown("<h1 style='color:#4A90E2;'>📑 振込リスト自動作成ツール</h1>", unsafe_allow_html=True)
st.markdown("アップロードしたCSVから発注先ごとの合計金額を算出し、Excelにまとめます。")
st.markdown("---")

uploaded_file = st.file_uploader("📂 CSVファイルをアップロード", type="csv")

if uploaded_file is not None:
    # 読み込み試行のための設定リスト: (エンコーディング, 区切り文字, 説明)
    # CP932を追加し、最も安全性の高い組み合わせを優先する
    read_attempts = [
        ("cp932", ",", "CP932 (カンマ区切り)"),
        ("shift_jis", ",", "Shift-JIS (カンマ区切り)"),
        ("utf-8", ",", "UTF-8 (カンマ区切り)"),
        ("cp932", "\t", "CP932 (タブ区切り)"),
        ("shift_jis", "\t", "Shift-JIS (タブ区切り)"),
    ]
    
    df = None
    read_success = False
    
    # ファイル読み込みの改善: 設定リストを順番に試す
    for encoding, sep, desc in read_attempts:
        try:
            # 毎回ファイルの先頭に戻す
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding, sep=sep)
            
            # 列が読み込めていれば成功とする (No columns to parse from file対策)
            if not df.empty and len(df.columns) > 1:
                st.info(f"✅ ファイルは {desc} として正常に読み込まれました。")
                read_success = True
                break
        except Exception:
            # 読み込みエラーが発生した場合は次の組み合わせを試す
            continue
            
    if not read_success:
         st.error("⚠️ CSVファイルからデータを読み込めませんでした。ファイルが空であるか、エンコーディング・区切り文字が特殊かもしれません。")
         st.stop() # 正常に処理を中断

    try:
        # 必須列のチェック
        required_cols = ['発注先名', '振込額']
        
        # 処理に必要な列がデータフレームに含まれているか確認
        missing_cols = [col for col in required_cols if col not in df.columns]

        if not missing_cols:
            # 必須列のみを選択し、発注先名でグループ化して振込額を合計
            # NOTE: .sum() の前に .astype(float) を実行して数値型に統一することを推奨
            # df['振込額'] = pd.to_numeric(df['振込額'], errors='coerce') 
            
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
        st.error("❌ データ集計処理中に予期せぬエラーが発生しました。")
        st.code(f"エラー詳細: {e}")

