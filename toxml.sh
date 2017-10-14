mkdir outputxml
for f in output/*.java
do
  srcML $f > ./outputxml/$(basename ${f%.*}).xml
done
