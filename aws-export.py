import os
import sys


def main():
    if not os.path.isfile(f'{os.getcwd()}/output.xlsx'):
        print('output.xlsx is not present')
        return
    if not os.path.isdir(f'{os.getcwd()}/temp/result'):
        print('result folder is not present')
        return

    append_name = sys.argv[1]

    #os.system(f"mv output.xlsx output{append_name}.xlsx")
    #os.system(f"aws s3 cp output{append_name}.xlsx s3://privado-testing")
    os.system(f"cd temp && sudo zip -r result{append_name}.zip result")
    os.system(f"aws s3 cp result{append_name}.zip s3://privado-testing")

    print("Successfully uploaded to s3 with name")


main()
