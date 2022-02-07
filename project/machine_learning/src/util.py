def label_counter(counter: dict) -> ( list, list ):
  all_labels = ['security', 'self-direction', 'benevolence', 'conformity', 'stimulation', 'power', 'achievement', 'tradition', 'universalism', 'hedonism']
  amount = []
  labels = []

  print('counter is ', counter)

  for key, item in counter.items():
    labels.append(key)
    amount.append(item)

  for l in all_labels:
    if l not in labels:
      labels.append(l)
      amount.append(0)

  return labels, amount


# counter = {"conformity": 12, "universalism": 15, "security": 1}
# res1, res2 = label_counter(counter)
# print(res1)
# print(res2)

