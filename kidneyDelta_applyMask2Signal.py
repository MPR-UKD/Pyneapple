from utils import *
import xlsxwriter
from PIL import Image
import glob

# Apply Masks to Delta Project Kidney and save signals to .xlsx


def Signal2CSV(img: nifti_img, path: str | None = None):
    csvdata = dict()
    data = None
    for idx in range(img.size[0]):
        for idy in range(img.size[1]):
            for idz in range(img.size[2]):
                if not math.isnan(img.array[idx, idy, idz, 0]):
                    data = (
                        np.vstack((data, img.array[idx, idy, idz, :]))
                        if data is not None
                        else img.array[idx, idy, idz, :]
                    )
    with open(r"bvalues.bval", "r") as f:
        bvalues = list(str(x) for x in f.read().split("\n"))
    df = pd.DataFrame(data, columns=bvalues)
    if path is not None:
        df.to_excel(path, index=False)
    else:
        return df


parent = r"E:\home\Thomas\Sciebo\Projekte\Kidney\Kidney_Delta\data_clean\.images"

subjects = [
    "_01_",
    "_02_",
    "_03_",
    "_04_",
    "_05_",
    "_06_",
    "_07_",
    "_08_",
    "_09_",
    "_10_",
    "_12_",
    "_13_",
    "_14_",
    "_15_",
]

# files = [
#     parent / "DeltaNiere_01_Delta026_sl3.nii",
#     parent / "DeltaNiere_01_Delta046_sl3.nii",
#     parent / "DeltaNiere_01_Delta066_sl3.nii",
#     parent / "DeltaNiere_01_Delta086_sl3.nii",
#     parent / "DeltaNiere_01_Delta106_sl3.nii",
# ]

parentMask = r"E:\home\Thomas\Sciebo\Projekte\Kidney\Kidney_Delta\data_clean\.mask_r"

data = list()
df_all = pd.DataFrame([], columns=["delta", "bval", "value"])
deltas = [26, 46, 66, 86, 106]

with xlsxwriter.Workbook("allDeltaAllSubjects.xlsx") as wrkbk_all:
    idx_all = 1
    wrksht_all = wrkbk_all.add_worksheet()
    wrksht_all.write_row(0, 0, ["delta", "bval", "value"])
    for nsub in subjects:
        idxD = 0
        idx = 1
        pMask = glob.glob(parentMask + "\*" + nsub + "*")
        mask = nifti_img(pMask[0])
        output = "all_Delta" + nsub + ".xlsx"
        with xlsxwriter.Workbook(output) as wrkbk:
            wrksht = wrkbk.add_worksheet()
            wrksht.write_row(0, 0, ["delta", "bval", "value"])
            for file in glob.glob(parent + "\*" + nsub + "*"):
                print(file)
                file = Path(file)
                nname = file.name.split(".")[0] + ".xlsx"
                img = nifti_img(file)
                img_masked = processing.applyMask2Image(img, mask)
                cdf = Signal2CSV(img_masked)
                for idxC, col in enumerate(cdf.columns):
                    for idxR, row in cdf.iterrows():
                        wrksht.write_row(
                            idx,
                            0,
                            [
                                deltas[idxD],
                                int(col),
                                (cdf.iloc[idxR, idxC] / cdf.iloc[idxR, 0]),
                            ],
                        )

                        wrksht_all.write_row(
                            idx_all,
                            0,
                            [
                                deltas[idxD],
                                int(col),
                                (cdf.iloc[idxR, idxC] / cdf.iloc[idxR, 0]),
                            ],
                        )
                        idx += 1
                        idx_all += 1
                idxD += 1
        wrkbk.close()
        wrkbk_all.close()
print("done")
