export PYTHONPATH="$PWD"

for f in tests/*.py; 
do echo "Running" $f;
   python3 $f;
   printf "\n\n"
done