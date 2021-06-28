def dataframe_to_nlu_file(dataf, write_path, text_col="text", label_col="intent"):
    """
    Converts a single DataFrame file with intents into a intents file for Rasa.
    Note that you cannot use this method to add entities.
    
    Usage:
    
    ```python
    import pandas as pd
    from rasa_nlu_examples.scikit import dataframe_to_nlu_file
    df = pd.DataFrame([
        {"text": "i really really like this", "intent": "positive"},
        {"text": "i enjoy this", "intent": "positive"},
        {"text": "this is not my thing", "intent": "negative"}
    ])
    dataframe_to_nlu_file(df, write_path="path/to/nlu.yml")
    ```
    
    This will yield a file with the following contents:
    
    ```yaml
    version: 2.0
    nlu:
    - intent: negative
      examples: |
      - this is not my thing
    - intent: positive
      examples: |
      - i really really like this
      - i enjoy this
    ```
    """
    result = {"version": str(2.0), "nlu": []}
    for idx, group in dataf.groupby(label_col):
        intent = group[label_col].iloc[0]
        result["nlu"].append(
            {
                "intent": intent,
                "examples": [t for t in group[text_col]],
            }
        )
    dump = (
        yaml.dump(result, sort_keys=False, width=1000)
        .replace("examples:", "examples: |")
        .replace("  -", "   -")
    )
    return pathlib.Path(write_path).write_text(dump)