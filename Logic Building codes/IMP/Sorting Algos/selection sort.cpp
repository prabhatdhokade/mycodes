// Selection Sort (O(n^2)) time complexity

#include<bits/stdc++.h>
using namespace std;

void SelectionSort(int arr[],int n){
    for(int i=0;i<n-2;i++){ // we need to n-2 passes
        int iMin = i;
        for(int j= i+1;j<n;j++){
            if(arr[j] < arr[iMin]) 
            iMin = j; // update the minimum element's  index
        }
        int temp = arr[i]; // swap the minimum element's index
        arr[i] = arr[iMin];
        arr[iMin] = temp;
    }
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    SelectionSort(arr,n);
    for(int i=0;i<n;i++){
        cout<<arr[i]<<" ";
    }
}