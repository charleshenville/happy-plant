# pip install tensorflowjs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflowjs import converters
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

# Load data from the text file
header = ['Date', 'Plant Type 1(ml)', 'Plant Type 2(ml)', 'Plant Type 3(ml)']
df = pd.read_csv('trainingData.csv', names=header, index_col=False)

# Convert 'Plant Type 2(ml)' column to numeric
df['Plant Type 2(ml)'] = pd.to_numeric(df['Plant Type 2(ml)'], errors='coerce')

# Drop rows with missing values, if any
df = df.dropna(subset=['Plant Type 2(ml)'])

# Set 'Date' column as the index
df.set_index('Date', inplace=True)

# Assuming you want to predict 'plant_type1', adjust this accordingly
target_column = 'Plant Type 2(ml)'

# Create a time series dataset
series = df[target_column]

# Plot the original series
plt.plot(series)
plt.xlabel('Date')

n = len(series)
x_ticks_frequency = n // 10  # Adjust the frequency of ticks based on your preference
plt.xticks(range(0, n, x_ticks_frequency), df.index[::x_ticks_frequency], rotation=45)

plt.ylabel(target_column)
plt.title(f'Time Series Plot of {target_column}')
plt.show()

# Build the dataset for training
T = 10  # Number of past values to predict the next value
X = []
Y = []

for t in range(len(series) - T):
    x = series[t:t + T]
    X.append(x)
    y = series[t + T]
    Y.append(y)

X = np.array(X).reshape(-1, T)
Y = np.array(Y)
N = len(X)
print("X.shape", X.shape, "Y.shape", Y.shape)

# Build the autoregressive linear model
i = Input(shape=(T,))
x = Dense(1)(i)
model = Model(i, x)
model.compile(
    loss='mse',
    optimizer=Adam(learning_rate=0.1),
)

# Train the model
r = model.fit(
    X[:-N // 2], Y[:-N // 2],
    epochs=80,
    validation_data=(X[-N // 2:], Y[-N // 2:]),
)

# Plot loss per iteration
plt.plot(r.history['loss'], label='loss')
plt.plot(r.history['val_loss'], label='val_loss')
plt.legend()

# Show the plots
plt.show()

# Forecast future values
validation_target = Y[-N // 2:]
validation_predictions = []

# First validation input
last_x = X[-N // 2]  # 1-D array of length T

while len(validation_predictions) < len(validation_target):
    p = model.predict(last_x.reshape(1, -1))[0, 0]  # 1x1 array -> scalar

    # Update the predictions list
    validation_predictions.append(p)

    # Make the new input
    last_x = np.roll(last_x, -1)
    last_x[-1] = p

# Plot the forecast
plt.plot(validation_target, label='forecast target')
plt.plot(validation_predictions, label='forecast prediction')
plt.legend()

# Show the plots
plt.show()

tfjs_path = './'
converters.save_keras_model(model, tfjs_path)
model.save('my_model.keras')