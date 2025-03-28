1. Jakie techniki fine-tuningu modeli językowych najlepiej dostosowują LLM do analizy logów Kubernetes?

Aby dostosować LLMy do analizy logów Kubernetes, najlepiej będzie zastosować takie techniki jak:

- Parameter-Efficient Fine-Tuning, który pozwala na dostosowanie modelu przy użyciu ograniczonych zasobów obliczeniowych i mniejszych zbiorów danych (https://learn.microsoft.com/en-us/azure/aks/concepts-fine-tune-language-models)

- Low-Rank Adaptation (LoRA) - przez zmniejsza zużycie pamięci i mocy obliczeniowej podczas fine-tuningu jest korzystne przy pracy z dużymi modelami na specjalistycznych danych, np. logach systemowych.

---

2. W jaki sposób Reinforcement Learning with Human Feedback (RLHF) wpływa na poprawność diagnoz generowanych przez model?

- Możliwa redukcja halucynacji, ponieważ  RLHF pomaga odrzucać odpowiedzi pozbawione podstaw w danych źródłowych
- Priorytetowanie odpowiedzi technicznie trafnych i użytecznych
- RLHF może pomóc modelowi zrozumieć, że np. “Pod evicted due to memory pressure” to istotniejszy sygnał niż “Liveness probe failed once” – czyli uczy model odróżniać realne problemy od “szumu” diagnostycznego
- Ludzie mogą ukarać odpowiedzi zawierające ryzykowne zalecenia (np. „Wyłącz walidację certyfikatu”), co zmniejsza szansę na niebezpieczne porady

---

3. Jakie dane i metryki są kluczowe przy fine-tuningu modeli NLP do analizy logów systemowych?

Kluczowe dla nas dane:
- Dane logów systemowych (surowe), które powinny zawierać pełne wpisy z informacjami takimi jak: timestamp, komponent, poziom logu (INFO, WARN, ERROR), wiadomość tekstowa;
- Logi etykietowane np. „normalne”, „anomalne”, „błąd krytyczny”, „problemy z siecią” (pod supervised learning);
- Logi z kontekstem, czyli przykłady składające się z sekwencji zdarzeń przed i po incydencie

Metryki:

- F1 score;
- Accuracy;
- Area Under ROC Curve;
- Time-to-detection / Latency;
- Model drift / concept drift monitoring

---

4 Jakie modele transformerowe (np. BERT for anomaly detection) najlepiej sprawdzają się w wykrywaniu nietypowych wzorców w logach Kubernetes?

- Modele BERT dostosowane do wykrywania anomalii na danych logów - model może nauczyć się rozpoznawać nietypowe wzorce w tych danych. (paper, w którym możemy znaleźc odpowiedzi: https://arxiv.org/pdf/2103.04475)

- Kombinacja autoenkoderów z Isolation Forest również może zwiększyć skuteczność wykrywania anomalii w danych logów.

---

6. Jak dynamicznie dostosowywać progi detekcji anomalii na podstawie historii incydentów?

Niektórymi z podejść do dynamicznego dostosowywania progów jest rolling window stats, czyli wyznaczanie progów na podstawie aktualnej dynamiki danych. Feedback loop, czyli zastosowanie metryk z historii incydentów . Zastosowanie modeli ML nauczonych klasyfikować anomalię na podstawie metryk (CPU, memory, disk I/O), metadanych (typ podu, namespace, labels), czy historii incydentów.

---

8. Jak HyDE (Hypothetical Document Embeddings) może poprawić dopasowanie kontekstu pytania do dokumentacji Kubernetes?

- lepsze dopasowanie semantyczne, dzięki temu, że HyDE pozwala na lepsze zrozumienie intencji użytkownika, co prowadzi do bardziej trafnych wyników wyszukiwania w dokumentacji Kubernetes;

- poprawa efektywności systemów RAG, dzięki generowaniu hipotetycznych dokumentów. Systemy mogą skuteczniej integrować zewnętrzną wiedzę, co przekłada się na bardziej precyzyjne odpowiedzi.;

- zastosowanie w specjalistycznych domenach, czyli w obszarach, gdzie tradycyjne modele mogą mieć trudności z generalizacją, takich jak złożona dokumentacja techniczna Kubernetes.

---

9. Jak połączyć sparse i dense retrieval, aby zwiększyć dokładność wyszukiwanych odpowiedzi w systemach RAG?

Aby połączyć te podejścia i zwiększyć dokładność wyszukiwania w systemach RAG, wypróbujemy następujące strategie:​

- Kaskadowe wyszukiwanie (cascading retrieval) (najpierw stosuje się jedną metodę wyszukiwania (np. rzadką) do wstępnego zawężenia zbioru dokumentów, a następnie drugą metodę (np. gęstą) do dalszej selekcji, co pozwala na efektywne przetwarzanie dużych zbiorów danych, łącząc precyzję zrozumienia kontekstu z dokładnością dopasowania słów kluczowych);

- Łączenie wyników z obu metod (równoczesne stosowanie obu metod wyszukiwania, a następnie łączenie ich wyników z odpowiednimi wagami, co umożliwia uwzględnienie zarówno precyzyjnego dopasowania słów kluczowych, jak i semantycznego podobieństwa);

- Wykorzystanie modeli hybrydowych (modeli, które integrują zarówno rzadkie, jak i gęste reprezentacje w jednym podejściu, np. Model SPLADE rozszerza reprezentacje rzadkie o dodatkowe terminy zidentyfikowane przez osadzenia gęste, co pozwala na lepsze radzenie sobie z problemem niedopasowania słownictwa: https://www.linkedin.com/pulse/retrieval-techniques-sparse-dense-hybrid-najeeb-khan-ph-d--wmtpc ).


---

10. Jakie algorytmy NLP najlepiej sprawdzają się w automatycznym kategoryzowaniu logów i alertów w środowiskach DevOps?

- Rekurencyjne sieci neuronowe (RNN) i ich ulepszone wersje, takie jak LSTM (Long Short-Term Memory), są zaprojektowane do przetwarzania sekwencji danych, co czyni je odpowiednimi do analizy logów, które często mają charakter sekwencyjny.

- Modele transformatorowe, takie jak BERT oraz GPT, które uczą się kontekstowych reprezentacji tekstu. Ich zdolność do rozumienia kontekstu i zależności między słowami sprawia, że są one skuteczne w analizie i kategoryzacji logów oraz alertów. Dużą zaletą jest ich wszechstronność.

- Techniki takie jak Word2Vec czy GloVe przekształcają słowa w wektory liczbowe, które odzwierciedlają ich znaczenie w kontekście. Dzięki temu podobne słowa mają zbliżone reprezentacje wektorowe, co ułatwia kategoryzację.

- Dodatkowo, algorytmy klastrowania grupują podobne dane bez potrzeby wcześniejszego etykietowania, co jest przydatne w odkrywaniu nowych wzorców w logach.