from datetime import timedelta

# Components of another_year add up to exactly 365 days
year = timedelta(days=365)
another_year = timedelta(weeks=40, days=84, hours=23, minutes=50, seconds=600)
print(year.eq(another_year))        # True
print(year.total_seconds())         # 31536000

test('timedelta: example #2')
print('min:', timedelta.min)        #
print('max:', timedelta.max)        #
print('res:', timedelta.resolution) #
ten_years = year.mul(10)
print(ten_years)                    # 3650d 00:00:00
nine_years = ten_years.sub(year)
print(nine_years)                   # 3285d 00:00:00
three_years = nine_years.floordiv(3)
print(three_years)                  # 1095d 00:00:00
