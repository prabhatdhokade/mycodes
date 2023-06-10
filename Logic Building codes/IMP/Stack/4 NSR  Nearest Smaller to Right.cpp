// Given an array of integers, find the closest (not considering distance, but value) smaller on rightof every element. If an element has no smaller on the right side, print -1.
// nearest smaller element to right, smaller to right
// input : 5
//  4 5 2 10 8
// output: 2 2 -1 8


#include<bits/stdc++.h>

using namespace std ;
/*
int main() 
{
    int n ;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++) {
        cin>>arr[i];
    }

    vector<int> vec;
    stack<int> s;

    for(int i= n-1; i >= 0; i--) {

        if( s.size() == 0) {
            vec.push_back(-1);
        }

        else if ( s.size() > 0 && s.top() < arr[i]) {
            vec.push_back(s.top());
        }

        else if ( s.size() > 0 && s.top() >= arr[i]) {
            while ( s.size() > 0 && s.top() >= arr[i]) {
                s.pop();
            }
            if ( s.size() == 0) {
                vec.push_back(-1);
            }
            else if (s.top() < arr[i]) {
                vec.push_back(s.top());
            }
        }
        s.push(arr[i]);
    }
    reverse (vec.begin(), vec.end());
    for(auto it = vec.begin(); it!=vec.end();it++) {
        cout<< *it<<" ";
    }

} */

vector<int> solve(int n,int arr[]){
    vector<int> v;
    stack<int> s;
    int j =n-1;
    while(j >=0){
        if(s.size() == 0) v.push_back(-1);

        else if(s.size() > 0 && s.top() < arr[j]) v.push_back(s.top());
        else if(s.size() > 0 && s.top() > arr[j] ){
            while(s.size() > 0 && s.top() > arr[j]){
                s.pop();
            }
            if(s.size() == 0) v.push_back(-1);
            else if(s.size() > 0 && s.top() < arr[j]) v.push_back(s.top());
        }
        s.push(arr[j]);
        j--;
    }
    reverse(v.begin() , v.end());
    return v;
}

int main() {
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    vector<int> v = solve(n,arr);
    for(auto it =v.begin(); it!= v.end();it++){
        cout<< *it<<" ";
    }
}