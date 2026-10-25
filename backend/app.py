import os
import pandas as pd
import joblib
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask("Superkart Sales Revenue Predictor")

# Load the serialized pipeline model
model_path = 'superkart_model.joblib'
model = joblib.load(model_path)

@app.route('/v1/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from request
        data = request.get_json(force=True)

        # Convert request JSON to DataFrame format
        input_df = pd.DataFrame([data])

        # Make prediction using our pre-trained pipeline
        prediction = model.predict(input_df)[0]

        # Return predicted sales total
        return jsonify({
            'Product_Store_Sales_Total': float(prediction)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/v1/predictbatch', methods=['POST'])
def predictbatch():
    try:
        # Get files from request
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file provided'}), 400

        # Convert file streams to pandas DataFrame
        input_df = pd.read_csv(file)

        # Make batch predictions
        predictions = model.predict(input_df)

        # Format response as a dict
        result = {str(i): float(pred) for i, pred in enumerate(predictions)}
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
