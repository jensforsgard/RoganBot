export PYTHONPATH="$PWD"

for file in $(find . -type f -name "test_*.py")
do echo "Running" $file;
   python3 $file;
   printf "\n\n";
done
