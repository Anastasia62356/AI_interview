#セルをファイルにする
#%%writefile app.py

import streamlit as st  #Streamli
import os #環境変数
from google import genai # gemini api

# 環境変数から API キーを取得
API_KEY = os.getenv('GEMINI_API_KEY')


# Gemini クライアント初期化
client = genai.Client(api_key=API_KEY)


# =========================================================
# セッションステートの初期化
# =========================================================
# セッションステートで自己PR生成結果を保持
if 'generated_ge' not in st.session_state:
    st.session_state["generated_ge"] = ""
# セッションステートでAI質問生成結果を保持
if 'generated_qu' not in st.session_state:
    st.session_state["generated_qu"] = ""
# セッションステートでAI評価生成結果を保持
if 'generated_ev' not in st.session_state:
    st.session_state["generated_ev"] = ""
# 追跡用ステート：生成中かどうかを管理
if 'is_generating' not in st.session_state:
    st.session_state["is_generating"] = False
# =========================================================


# ----------------------------------------
# メイン処理
# ----------------------------------------
#サイドバー
st.sidebar.title("設定")

#モード選択ラジオボタン
user_mode = st.sidebar.radio("モード", ["自己PRジェネレータ", "AI面接質問","AI面接評価"])


# ----------------------------------------
# 自己PRジェネレータ
# ----------------------------------------
def PR_GE():

    #保持出力内容表示フラグ
    fg = 0

    #利用シーンラジオボタン
    user_use = st.sidebar.radio("利用シーン", ["新卒", "転職","学校面接"])


    #職種学科入力
    user_job_or_subject = st.sidebar.text_input("職種または学科")


    #文字数スライダー
    max_char_count = st.sidebar.slider("文字数を選択", 150, 300, 450) + 20
    min_char_count = max_char_count - 40


    #キーワード入力
    user_keywords_ge = st.text_area(
        "キーワード (強み、スキル、実績などを複数行で入力)",
        placeholder="例:\nPythonとデータ分析スキル\nチームリーダー経験3年\n顧客満足度20%向上に貢献"
    )

    #キーワードリスト化
    keyword_list = [k.strip() for k in user_keywords_ge.split('\n') if k.strip()]
    keywords_formatted = "\n- " + "\n- ".join(keyword_list)

    #エピソード入力
    user_episode = st.text_area(
        "実績の詳細エピソード (PRに含めたい具体的な背景・行動・結果)",
        placeholder="例:\n前職でデータ収集の自動化を提案。Pythonスクリプトを自作し、作業時間を週10時間削減。この実績を元にPRを構成してください。"
    )



    #Gemini送信プロント
    prompt = f"""
    あなたは、ユーザーの成功のために、**文字数と全ての制約を絶対厳守するプロフェッショナルなキャリアコンサルタント**です。

    【絶対厳守ルール】
    1. **生成する文章は、**上限**{max_char_count}字**を**絶対に超えてはいけません**。さらに、**{min_char_count}字以上**（上限から40字を引いた範囲内）に収めることを**絶対厳守**してください。
    2. **生成する文章句読点を使用し、**空白、改行を一切使用せず**、文字のみで構成すること。
    3. **回答は自己PRの本文のみ**とし、「承知いたしました」などの前置きや、文字数に関する注釈、タイトルは一切付けないこと。

    【生成タスク】
    以下の【前提条件】と【キーワード】を基に、魅力的でターゲットに響く{user_use}活動用の自己PRを**厳密に{min_char_count}字から{max_char_count}字の間**で作成してください。

    【前提条件】
    利用シーン - {user_use}
    職種または学科 - {user_job_or_subject}
    エピソード - {user_episode}

    【キーワード】
    キーワード - {keywords_formatted}
    """



    # コールバック関数: API呼び出し前に実行され、フラグをTrueにする
    def set_generating_flag():
        st.session_state["is_generating"] = True
        st.session_state["generated_ge"] = "" # 新しい生成の前に以前の結果をクリア

    # 送信ボタン。 is_generatingがTrueの間はボタンを無効化
    # on_clickハンドラを追加し、ボタンが押された瞬間にフラグをTrueに設定
    if st.button("自己PRを生成する", disabled=st.session_state["is_generating"], on_click=set_generating_flag):
        if not user_keywords_ge:
            st.warning("キーワードを最低一つ入力してください。")
            st.session_state["is_generating"] = False
        elif not user_episode:
            st.warning("エピソードを入力してください。")
            st.session_state["is_generating"] = False
        elif not user_job_or_subject:
            st.warning("職種または学科を入力してください。")
            st.session_state["is_generating"] = False
        else:
            # on_clickでフラグ設定済みのため、ここではスピナー表示とAPI呼び出しのみを行う
            with st.spinner("Geminiが自己PRを作成中..."):
                for k in range(5):
                    try:
                        # Gemini API呼び出し
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )

                        # 生成結果の文字数をカウント
                        generated_text = response.text.strip()
                        char_count = len(generated_text)

                        #文字数の条件
                        if min_char_count <= char_count <= max_char_count:
                            # 条件を満たした場合のみ表示・保存
                            st.session_state["generated_ge"] = generated_text
                            fg = 1

                            st.success("🎉 自己PRが完成しました！")
                            st.subheader("生成された自己PR")
                            st.write(st.session_state["generated_ge"])
                            break
                        else:
                            # 条件を満たさない場合は再生成
                            st.warning(f"再生成します（現在の文字数: {char_count}文字）")
                            continue

                    except Exception as e:
                        st.error(f"API呼び出し中にエラーが発生しました: {e}")
                        break

                    finally:
                        # 成功・失敗を問わずフラグを戻す
                        st.session_state["is_generating"] = False



    #保持出力内容表示
    if  st.session_state["generated_ge"] != "" and fg != 1:
      st.success("🎉 自己PRが完成しました！")
      st.subheader("生成された自己PR")
      st.write(st.session_state["generated_ge"])


# ----------------------------------------
# AI面接質問
# ----------------------------------------
def AI_QU():

    #保持出力内容表示フラグ
    fg = 0

    #利用シーンラジオボタン
    user_use = st.sidebar.radio("利用シーン", ["新卒", "転職","学校面接"])

    #職種学科入力
    user_job_or_subject = st.sidebar.text_input("職種または学科")

    #質問数スライダー
    question_count = st.sidebar.slider("質問数", 1, 5,10)

    #キーワード入力
    user_keywords_qu = st.text_area(
        "キーワード (強み、スキル、実績などを複数行で入力)",
        placeholder="例:\nPythonとデータ分析スキル\nチームリーダー経験3年\n顧客満足度20%向上に貢献"
    )

    #キーワードリスト化
    keyword_list = [k.strip() for k in user_keywords_qu.split('\n') if k.strip()]
    keywords_formatted = "\n- " + "\n- ".join(keyword_list)

    #自己PR入力
    user_pr = st.text_area(
        "自己PRの素材入力（AI面接官に伝えたい実績・自己PR）",
        placeholder="例:\n前職でデータ収集の自動化を提案し、Pythonスクリプトを自作して週10時間の作業削減を実現しました。自己PRを元にAIが面接想定問題を出題します"
    )

    prompt = f"""
    あなたは、利用シーン**{user_use}**の応募職種（または学科）**{user_job_or_subject}**の採用を任された**厳格で経験豊富な面接官**です。

    【生成タスク】
    以下の【キーワード】と【自己PR】を細かく分析し、このPRの**真実性（再現性）**、**深さ（思考力）**、および**応用力（ポテンシャル）**を試すための、具体的で深掘りした質問を**5つ**作成してください。

    【制約】
    1. **質問は{question_count}つ**とし、必ず**番号付きリスト**（1., 2.など）で出力すること。
    2. **回答は質問文のみ**とし、「承知いたしました」などの前置きや、質問の解説、タイトルは一切付けないこと。
    3. 特に、自己PRで語られた**具体的な行動**や**実績の数値**に対して疑問を投げかける形式の質問を優先すること。

    【キーワード】
    キーワード - {keywords_formatted}

    【自己PR】
    自己PR - {user_pr}
    """

    # コールバック関数: API呼び出し前に実行され、フラグをTrueにする
    def set_generating_flag():
        st.session_state["is_generating"] = True
        st.session_state["generated_qu"] = "" # 新しい生成の前に以前の結果をクリア

    # 送信ボタン。 is_generatingがTrueの間はボタンを無効化
    # on_clickハンドラを追加し、ボタンが押された瞬間にフラグをTrueに設定
    if st.button("面接質問を生成する", disabled=st.session_state["is_generating"], on_click=set_generating_flag) :
        if not user_keywords_qu:
            st.warning("キーワードを最低一つ入力してください。")
            st.session_state["is_generating"] = False
        elif not user_pr:
            st.warning("自己PRを入力してください。")
            st.session_state["is_generating"] = False
        elif not user_job_or_subject:
            st.warning("職種または学科を入力してください。")
            st.session_state["is_generating"] = False
        else:
            # on_clickでフラグ設定済みのため、ここではスピナー表示とAPI呼び出しのみを行う
            with st.spinner("Geminiが質問を作成中..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents = prompt
                      )

                    # 結果をセッションステートに保存
                    st.session_state["generated_qu"] = response.text
                    fg = 1

                    # 結果の表示
                    st.success("🎉 面接想定質問が完成しました！")
                    st.subheader("AI面接官の質問リスト")
                    st.write(st.session_state["generated_qu"])

                except Exception as e:
                    st.error(f"API呼び出し中にエラーが発生しました: {e}")

                finally:
                    # 処理の成功/失敗に関わらず、最後にフラグをFalseに戻す
                    st.session_state["is_generating"] = False

    
    #保持出力内容表示
    if  st.session_state["generated_qu"] != "" and fg != 1:
        st.success("🎤 面接想定質問が完成しました！")
        st.subheader("AI面接官の質問リスト")
        st.write(st.session_state["generated_qu"])


# ----------------------------------------
# AI面接評価
# ----------------------------------------                
def AI_EV():

    #保持出力内容表示フラグ
    fg = 0

    #利用シーンラジオボタン
    user_use = st.sidebar.radio("利用シーン", ["新卒", "転職","学校面接"])

    #職種学科入力
    user_job_or_subject = st.sidebar.text_input("職種または学科")

    #評価の厳しさスライダー
    strict_level = st.sidebar.slider("評価の厳しさ", 1, 3, 5)

    #質問文入力
    user_question = st.text_area(
    "質問文(面接官に聞かれる質問を入力)",
    placeholder="例:\n自己PRでアピールできる強みを教えてください"
    )

    #回答入力
    user_answer = st.text_area(
    "回答（質問に対する回答を入力）",
    placeholder="例:\n私の強みは責任感の強さです。どんな状況でも最後までやり遂げる姿勢を大切にしています。"
    )


    prompt = f"""
    あなたは、利用シーン **{user_use}** の応募職種（または学科） **{user_job_or_subject}** の採用を任された、  
    **厳格で経験豊富な面接官** です。
    
    【生成タスク】  
    以下の【質問文】を元に【回答】を細かく分析し、  
    **以下の「評価項目」に基づき、100点満点で採点**してください。
    
    ---
    
    【評価方針】  
    評価の厳しさレベル：**{strict_level} / 5**  
    （数値が高いほどより厳格・シビアに採点・指摘を行ってください）
    
    ### 評価厳しさレベル別の基準
    | レベル | 採点・コメント方針 |
    |:-------:|:------------------|
    | **1（甘口）** | 積極的に良い点を評価し、減点は最小限。言葉遣いも柔らかく、励ますようなコメントを中心にする。 |
    | **2（やや甘口）** | 長所を重視しつつ、軽い改善点を指摘。全体的にポジティブなトーンを維持。 |
    | **3（中立）** | バランスの取れた評価。良い点・改善点の両方を明確に述べ、公平に採点する。 |
    | **4（やや辛口）** | 内容の深さ・論理性を厳しく精査し、不十分な部分を具体的に指摘する。点数もやや厳しめに。 |
    | **5（激辛・厳格）** | 専門家レベルの基準で評価。曖昧・抽象的な表現を強く減点し、具体性・一貫性・説得力を厳密に求める。 |
    
    ---
    
    ### 評価項目
    1. **論理性と構造 (30点)**：回答の主張と根拠が明確に繋がり、構造化されているか。  
    2. **具体性と深さ (40点)**：抽象論に終わらず、具体的なエピソードやデータ、独自の視点が含まれているか。  
    3. **職務（または学科）との関連性 (30点)**：応募者がこの職種や分野で活躍できるポテンシャルを感じさせる内容か。
    
    ---
    
    ### アウトプット形式  
    上記の分析と採点に基づき、**必ず以下の【見出し形式】で**出力してください。
    
    ---
    ## 総合点
    **(合計点 / 100点)**
    
    ---
    ## 詳細フィードバック
    * **良い点**
        * (回答の評価点や長所を具体的に1点目)
        * (回答の評価点や長所を具体的に2点目)
    * **改善点**
        * (回答の不足点や改善が必要な点を具体的に1点目)
        * (回答の不足点や改善が必要な点を具体的に2点目)
    ---
    ## 総評
        * 全体として(回答全体の印象をまとめる)。
      
    
    ---
    【質問文】
    質問文 - {user_question}
    
    【回答】
    回答 - {user_answer}
    """

      # コールバック関数: API呼び出し前に実行され、フラグをTrueにする
    def set_generating_flag():
        st.session_state["is_generating"] = True
        st.session_state["generated_ev"] = "" # 新しい生成の前に以前の結果をクリア

    # 送信ボタン。 is_generatingがTrueの間はボタンを無効化
    # on_clickハンドラを追加し、ボタンが押された瞬間にフラグをTrueに設定
    if st.button("評価を生成する", disabled=st.session_state["is_generating"], on_click=set_generating_flag) :
        if not user_question:
            st.warning("質問文を入力してください。")
            st.session_state["is_generating"] = False
        elif not user_answer:
            st.warning("回答を入力してください。")
            st.session_state["is_generating"] = False
        elif not user_job_or_subject:
            st.warning("職種または学科を入力してください。")
            st.session_state["is_generating"] = False
        else:
            # on_clickでフラグ設定済みのため、ここではスピナー表示とAPI呼び出しのみを行う
            with st.spinner("Geminiが評価を作成中..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents = prompt
                      )

                    # 結果をセッションステートに保存
                    st.session_state["generated_ev"] = response.text
                    fg = 1

                    # 結果の表示
                    st.success("🎉 評価が完成しました！")
                    st.subheader("AI面接官の評価")
                    st.write(st.session_state["generated_ev"])

                except Exception as e:
                    st.error(f"API呼び出し中にエラーが発生しました: {e}")

                finally:
                    # 処理の成功/失敗に関わらず、最後にフラグをFalseに戻す
                    st.session_state["is_generating"] = False

         #保持出力内容表示
    if  st.session_state["generated_ev"] != "" and fg != 1 :
        st.success("🎉 評価が完成しました！")
        st.subheader("AI面接官の評価")
        st.write(st.session_state["generated_ev"])


# ----------------------------------------
# メイン処理
# ----------------------------------------
#タイトル
st.title(user_mode)

#画面遷移
if   user_mode == "自己PRジェネレータ":
     PR_GE()
elif user_mode == "AI面接質問":
     AI_QU()
elif user_mode == "AI面接評価":
     AI_EV()
