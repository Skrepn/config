import unittest
import subprocess
import sys

# Имя исходного файла
PROGRAM_NAME = 'main.py'

class TestSimple(unittest.TestCase):

    # Запускает программу в отдельном процессе
    def send_data(self, text):
        process = subprocess.Popen(
            [sys.executable, PROGRAM_NAME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=text)
        return stdout, stderr

    # 1. Тест простых чисел
    def test_numbers(self):
        data = "A := 10\nB := -5"
        out, err = self.send_data(data)

        self.assertIn("<A>10</A>", out)
        self.assertIn("<B>-5</B>", out)
        print("Тест чисел: РАБОТАЕТ")

    # 2. Тест массивов
    def test_arrays(self):
        data = "LIST := << 1, 2, 3 >>"
        out, err = self.send_data(data)

        self.assertIn("<LIST>", out)
        self.assertIn("<item>1</item>", out)
        self.assertIn("<item>2</item>", out)
        self.assertIn("<item>3</item>", out)
        print("Тест массивов: РАБОТАЕТ")

    # 3. Тест словарей
    def test_dictionaries(self):
        data = "DICT := [ X => 100, Y => 200 ]"
        out, err = self.send_data(data)

        self.assertIn("<X>100</X>", out)
        self.assertIn("<Y>200</Y>", out)
        print("Тест словарей: РАБОТАЕТ")

    # 4. Тест констант (объявление и использование)
    def test_constants(self):
        data = """
        CONST := 50
        RESULT := #(CONST)
        """
        out, err = self.send_data(data)

        self.assertIn("<CONST>50</CONST>", out)
        self.assertIn("<RESULT>50</RESULT>", out)
        print("Тест констант: РАБОТАЕТ")

    # 5. Тест вложенности (массив внутри словаря и наоборот)
    def test_nesting(self):
        data = """
        COMPLEX := [
            ARR => << 1, 2 >>,
            SUBDICT => [ Z => 3 ]
        ]
        """
        out, err = self.send_data(data)

        self.assertIn("<ARR>", out)
        self.assertIn("<item>1</item>", out)
        self.assertIn("<SUBDICT>", out)
        self.assertIn("<Z>3</Z>", out)
        print("Тест вложенности: РАБОТАЕТ")

    # 6. Тест комментариев
    def test_comments(self):
        data = """
        * Это комментарий
        VAL := 777
        """
        out, err = self.send_data(data)

        self.assertIn("<VAL>777</VAL>", out)
        # Убеждаемся, что текст комментария не попал в вывод
        self.assertNotIn("Это комментарий", out)
        print("Тест комментариев: РАБОТАЕТ")

if __name__ == '__main__':
    # Запуск тестов
    unittest.main()
