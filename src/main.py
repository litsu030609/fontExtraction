import sys
from fontTools.ttLib import TTFont
from fontTools.merge import Merger
from fontTools.ttLib import TTCollection
import subprocess

def show(font_path):
    
    # ttfファイルの場合
    if font_path.endswith(".ttf"):
        font = TTFont(font_path)
        cmap = font['cmap'].getBestCmap()

        print("=== 使用可能文字 ===")
        with open("font_chars.txt", "w", encoding="utf-8") as f:
            for idx, codepoint in enumerate(cmap, start=1):
                ch = chr(codepoint)
                print(ch, end="")
                f.write(ch)
                
                # 100文字ごとに改行
                if idx % 100 == 0:
                    print()
                    f.write("\n")
            print("\n")

        print("総文字数:", len(cmap))
        
    # ttcファイルの場合
    if font_path.endswith(".ttc"):
        ttc = TTCollection(font_path)
        for i, font in enumerate(ttc.fonts):
            name = font['name'].getDebugName(1)  # Font Family Name
            print(i, name)
            print(f"=== フォント {name} ===")
            cmap = font['cmap'].getBestCmap()
            with open(f"font_chars_{name}.txt", "w", encoding="utf-8") as f:
                for idx, codepoint in enumerate(cmap, start=1):
                    ch = chr(codepoint)
                    print(ch, end="")
                    f.write(ch)
                    
                    # 100文字ごとに改行
                    if idx % 100 == 0:
                        print()
                        f.write("\n")
                print("\n")

            print("総文字数:", len(cmap))


def extraction(font_path, input_txt, output_font):
    # ttfファイルの場合
    if font_path.endswith(".ttf"):
        font = TTFont(font_path)
        cmap = font['cmap'].getBestCmap()

        with open(input_txt, encoding="utf-8") as f:
            text = f.read()

        valid_chars = ""
        for c in text:
            if ord(c) in cmap:
                valid_chars += c
            else:
                print(f"[LOG] '{c}' はフォントに存在しません")

        if valid_chars == "":
            print("抽出可能文字なし")
            return

        print("抽出文字:", valid_chars)

        subprocess.run([
            "pyftsubset",
            font_path,
            f"--text={valid_chars}",
            f"--output-file={output_font}"
        ])

        print("subsetフォント生成:", output_font)
    # ttcファイルの場合
    if font_path.endswith(".ttc"):
        subset_fonts = []
        ttc = TTCollection(font_path)
        for i, font in enumerate(ttc.fonts):
            name = font['name'].getDebugName(1)  # Font Family Name
            print(f"=== フォント {name} ===")
            cmap = font['cmap'].getBestCmap()

            with open(input_txt, encoding="utf-8") as f:
                text = f.read()

            valid_chars = ""
            for c in text:
                if ord(c) in cmap:
                    valid_chars += c
                else:
                    print(f"[LOG] '{c}' はフォントに存在しません")

            if valid_chars == "":
                print("抽出可能文字なし")
                continue

            print("抽出文字:", valid_chars)

            output_font = f"_{name}.ttf"

            subprocess.run([
                "pyftsubset",
                font_path,
                f"--font-number={i}",
                f"--text={valid_chars}",
                f"--output-file={output_font}"
            ])
            subset_fonts.append(TTFont(output_font))

            print("subsetフォント生成:", output_font)
        if not subset_fonts:
            print("抽出可能なフォントがなかったため subset.ttc は作成しません")
            return

        # TTCollection() はパス/ファイルを受け取るため、空で作って fonts を差し込む
        new_ttc = TTCollection()
        new_ttc.fonts = subset_fonts
        new_ttc.save("subset.ttc")

# def join(font_a, font_b, output):
#     merger = Merger()
#     merged = merger.merge([font_a, font_b])
#     merged.save(output)
#     print("フォント結合:", output)


def main():
    if len(sys.argv) < 2:
        print("usage:")
        print(" フォントで使用できる文字をテキストファイルに出力")
        print(" show exsample.ttf")
        print(" フォントから特定の文字を抽出してサブセットフォントを作成")
        print(" extraction exsample.ttf input.txt output.ttf")
        # print(" 複数のフォントを結合")
        # print(" join A.ttf B.ttf output.ttf")
        return

    cmd = sys.argv[1]

    if cmd == "show":
        show(sys.argv[2])

    elif cmd == "extraction":
        extraction(sys.argv[2], sys.argv[3], sys.argv[4])

    # elif cmd == "join":
    #     join(sys.argv[2], sys.argv[3], sys.argv[4])

    else:
        print("unknown command")


if __name__ == "__main__":
    main()