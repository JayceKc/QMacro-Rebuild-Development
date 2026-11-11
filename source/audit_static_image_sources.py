"""Read-only name check limited to the supplied original directory."""
from pathlib import Path,PureWindowsPath
import collections,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    source=Path(r'D:\2.12-台服繁體-右鍵走路')
    dep=PROJECT/'verification/asset-dependencies.json'
    data=json.loads(dep.read_text(encoding='utf8'))
    wanted=sorted({r['filename'].casefold() for r in data['references'] if r['status']=='missing'})
    listing=subprocess.run(['rg','--files',str(source)],capture_output=True,encoding='utf8',check=True)
    paths=listing.stdout.splitlines()
    found=[p for p in paths if PureWindowsPath(p).name.casefold() in wanted]
    report={'source_root':str(source),'listed_files':len(paths),'wanted_names':wanted,'found_paths':found,
            'dependency_report_sha256':hashlib.sha256(dep.read_bytes()).hexdigest(),
            'scope':'Named original directory and recovered attachment catalog only; not an exhaustive scan of all drives or encoded/unprovided sources.'}
    (PROJECT/'verification/static-image-source-search.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'wanted_names':len(wanted),'listed_files':len(paths),'found_paths':len(found)}))


if __name__=='__main__':main()
