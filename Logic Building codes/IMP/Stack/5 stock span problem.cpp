/*The stock span problem is a financial problem where we have a series of n daily price quotes for a stock and we need to calculate span of stock’s price for all n days.
The span Si of the stock’s price on a given day i is defined as the maximum number of consecutive days just before the given day, for which the price of the stock on the current day is less than or equal to its price on the given day.
For example, if an array of 7 days prices is given as {100, 80, 60, 70, 60, 75, 85}, then the span values for corresponding 7 days are {1, 1, 1, 2, 1, 4, 6} */
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

    stack <pair<int,int>> s;  // we'll store values in pair(first -> value, second -> index)
    vector < int > vec;

    for(int i =0; i < n; i++) {

        if(s.size()== 0) {
            vec.push_back(-1);
        }

        else if ( s.size() > 0 && s.top().first > arr[i]) { // compare with the value
            vec.push_back(s.top().second);  // pushback the index for further calculation
        }

        else if ( s.size() > 0 && s.top().first <= arr[i]) {
            while ( s.size() > 0 && s.top().first <= arr[i]) {
                s.pop();
            } 

            if ( s.size() == 0) {
                vec.push_back(-1);
            }

            else
                vec.push_back(s.top().second);  // we'll only store thn index values in vector
        }
        s.push({arr[i],i});             // we have to push the arr[i] and index
    }
    for(int i =0 ; i< vec.size(); i++) {
      vec[i] = i - vec[i];
        cout<< vec[i] << " ";
    }

    
} 
*/

// same as nearest greater to left 

vector<int> solve(int n,int arr[]){
    vector<int>v;
    stack<pair<int,int>> s;  // imp
    int j=0;
    while(j<n){

        if(s.size() == 0){
            v.push_back(-1);
        }
        else if(s.size() > 0 && s.top().first >= arr[j]) v.push_back(s.top().second); // imp last step

        else if(s.size() > 0 && s.top().first < arr[j]){
            while(s.size() > 0 && s.top().first < arr[j]){
                s.pop();
            }
            if(s.size() == 0){
            v.push_back(-1);
            }
            else if(s.size() > 0 && s.top().first >= arr[j]) v.push_back(s.top().second);

        }
        s.push({arr[j] ,j});  // imp
        j++;
    }
    for(int i=0;i<v.size();i++){   // VVVVIMP
        //v[i] = i - v[i];
    }
    return v;
}

int main() {
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    vector<int> v =solve(n,arr);
    for(int i=0;i<v.size();i++){
        cout<< v[i]<< " ";
    }
}